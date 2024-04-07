import sys
import requests
import base64
import json
import uuid

from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QImage, QImageReader
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication
from PyQt5.QtWidgets import QInputDialog, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
# from utils import generate_uuid


class MobileApp(QMainWindow):
    """
    This class is a subpart of main window.
    The purpose of this class is to register a new case and
    save it in Firebase Database.

    After selecting the image you'll see in left side of window.
    If you are able to see image that means algo is able to find
    facial points in image. Otherwise you'll get error.

    If you encounter any error while saving the image, check the logs
    which are being printed.
    """

    def __init__(self):
        """
        We are initializing few things we would need.
            name -> Name of person whose case has to be registered.
            age -> Age of the person
            mob -> Mobile number that will be contacted after the person is found.
            father_name -> Father's name of the person
            image -> image of the person
        """
        super().__init__()
        self.title = "Submit Image"
        self.icon_path = "../resources/icon.png"
        self.location = None
        self.name = None
        self.mobile = None
        self.image = None
        self.key_points = None
        self.initialize()

    def initialize(self):
        """
        This method contains button to select the image and
        also register the case.

        The select image button is connected to openFileNameDialog method.

        The save button is connected to save method (within the class).

        -> If you are chaning the window size make sure to align the buttons
            correctly.
        """
        self.setWindowIcon(QtGui.QIcon(self.icon_path))
        self.setFixedSize(400, 700)
        self.setWindowTitle(self.title)

        upload_image_bt = QPushButton("Image", self)
        upload_image_bt.move(150, 250)
        upload_image_bt.clicked.connect(self.openFileNameDialog)

        save_bt = QPushButton("Save ", self)
        save_bt.move(150, 640)
        save_bt.clicked.connect(self.save)

        self.get_name()
        self.get_mobile_num()
        self.get_location()
        self.show()

    def get_name(self):
        """
        This method reads the input name from text field in GUI.
        """
        locatex_label = QLabel(self)
        locatex_label.setText("<h1>LocateX</h1>")
        locatex_label.setAlignment(Qt.AlignCenter)
        locatex_label.move(150, 20)
        self.name_label = QLabel(self)
        self.name_label.setText("Your Name:")
        self.name_label.move(80, 80)

        self.name = QLineEdit(self)
        self.name.move(150, 80)

    def get_mobile_num(self):
        """
        This method reads mob number from text field in GUI.
        """
        self.mobile_label = QLabel(self)
        self.mobile_label.setText("Mobile:")
        self.mobile_label.move(80, 120)

        self.mobile = QLineEdit(self)
        self.mobile.move(150, 120)

    def get_location(self):
        """
        This method reads the input name from text field in GUI.
        """
        self.location_label = QLabel(self)
        self.location_label.setText("Location:")
        self.location_label.move(80, 160)

        self.location = QLineEdit(self)
        self.location.move(150, 160)

    def get_facial_points(self, image_url) -> list:
        """
        This method passes the base64 form iamge to get facialkey points.

        Returns
        -------
         list
        """
        URL = "http://localhost:8002/image"
        f = [("image", open(image_url, "rb"))]
        try:
            result = requests.post(URL, files=f)
            if result.status_code == 200:
                return json.loads(result.text)["encoding"]
            else:
                QMessageBox.about(self, "Error", "Couldn't find face in Image")
                return None
        except Exception as e:
            QMessageBox.about(self, "Error", "Couldn't connect to face encoding API")
            return None

    def openFileNameDialog(self):
        """
        This method is triggered on button click to select image.

        When an image is selected its local URL is captured.
        After which it is passed through read_image method.
        Then it is converted to base64 format and facial keypoints are
        generated for it.

        If keypoints are not found in the image then you'll get a dialogbox.
        """
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "jpg file (*.jpg)",
            options=options,
        )

        if self.fileName:
            self.key_points = self.get_facial_points(self.fileName)
            if self.key_points:
                label = QLabel(self)
                pixmap = QPixmap(self.fileName)
                pixmap = pixmap.scaled(320, 350)
                label.setPixmap(pixmap)
                label.resize(250, 280)
                label.move(75, 300)
                label.show()

    def get_entries(self):
        """
        A check to make sure empty fields are not saved.
        A case will be uniquely identified by these fields.
        """
        entries = {}
        if (
            self.mobile.text() != ""
            and self.name.text() != ""
            and self.location.text() != ""
        ):
            entries["name"] = self.name.text()
            entries["location"] = self.location.text()
            entries["mobile"] = self.mobile.text()
            return entries
        else:
            return None

    def save_to_db(self, entries):
        URL = "http://localhost:8001/user_submission"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        byte_content = open(self.fileName, "rb").read()
        base64_bytes = base64.b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")

        entries["image"] = base64_string
        try:
            res = requests.post(URL, json.dumps(entries), headers=headers)
            if res.status_code == 200:
                QMessageBox.about(self, "Success", "Saved successfully")
            else:
                QMessageBox.about(self, "Error", "Something went wrong while saving")
                print(res.text)
        except Exception as e:
            print(str(e))
            QMessageBox.about(self, "Error", "Couldn't connect to database")

    def generate_uuid(self) -> str:
        """Generates random uui4"""
        return str(uuid.uuid4())

    def save(self):
        """
        Save method is triggered with save button on GUI.

        All the parameters are passed to a db methods whose task is to save
        them in db.

        If the save operation is successful then you'll get True as output and
        a dialog message will be displayed other False will be returned and
        you'll get appropriate message.

        """
        entries = self.get_entries()
        if entries:
            entries["face_encoding"] = self.key_points
            entries["sub_id"] = self.generate_uuid()
            self.save_to_db(entries)
        else:
            QMessageBox.about(self, "Error", "Please fill all entries")


app = QApplication(sys.argv)
style = """
    QWidget {
    background-color: #2c3e50;
    background-image: url('https://www.lifewire.com/thmb/Kv2e3RqYmPj4iya7GBgW8SyTP_Q=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-1421460958-e3be73d7975343d7986e839fefe44be9.jpg');
    background-repeat: no-repeat;
    background-position: center;
}

QLabel {
    color: #ecf0f1;
}

QListView {
    background-color: #34495e;
}

QPushButton {
    color: #fff;
    background-color: #2980b9;
    border: 1px solid #3498db;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 10pt;
}

QPushButton:hover {
    background-color: #3498db;
    border-color: #2980b9;
}

QLineEdit {
    padding: 6px;
    color: #fff;
    background-color: #34495e;
    border: 2px solid #3498db;
    border-radius: 5px;
}

QMessageBox {
    background-color: #2c3e50;
    color: #ecf0f1;
    border: 2px solid #3498db;
}

QMessageBox QPushButton {
    color: #fff;
    background-color: #2980b9;
    border: 1px solid #3498db;
    border-radius: 5px;
    padding: 6px 12px;
    font-weight: bold;
}

QMessageBox QPushButton:hover {
    background-color: #3498db;
    border-color: #2980b9;
}
"""


app.setStyleSheet(style)
w = MobileApp()
sys.exit(app.exec())
