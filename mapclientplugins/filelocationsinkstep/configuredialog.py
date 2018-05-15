
import os

from PySide import QtGui
from mapclientplugins.filelocationsinkstep.ui_configuredialog import Ui_ConfigureDialog

INVALID_STYLE_SHEET = 'background-color: rgba(239, 0, 0, 50)'
DEFAULT_STYLE_SHEET = ''


class ConfigureDialog(QtGui.QDialog):
    """
    Configure dialog to present the user with the options to configure this step.
    """

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self._ui = Ui_ConfigureDialog()
        self._ui.setupUi(self)

        # Keep track of the previous identifier so that we can track changes
        # and know how many occurrences of the current identifier there should
        # be.
        self._previousIdentifier = ''
        # Set a place holder for a callable that will get set from the step.
        # We will use this method to decide whether the identifier is unique.
        self.identifierOccursCount = None

        self._workflow_location = None
        self._previousLocation = ''

        self._makeConnections()

    def _makeConnections(self):
        self._ui.lineEdit0.textChanged.connect(self.validate)
        self._ui.pushButtonFileChooser.clicked.connect(self._fileChooserClicked)

    def accept(self):
        """
        Override the accept method so that we can confirm saving an
        invalid configuration.
        """
        result = QtGui.QMessageBox.Yes
        if not self.validate():
            result = QtGui.QMessageBox.warning(self, 'Invalid Configuration',
                'This configuration is invalid.  Unpredictable behaviour may result if you choose \'Yes\', are you sure you want to save this configuration?)',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            QtGui.QDialog.accept(self)

    def setWorkflowLocation(self, location):
        self._workflow_location = location

    def validate(self):
        """
        Validate the configuration dialog fields.  For any field that is not valid
        set the style sheet to the INVALID_STYLE_SHEET.  Return the outcome of the
        overall validity of the configuration.
        """
        # Determine if the current identifier is unique throughout the workflow
        # The identifierOccursCount method is part of the interface to the workflow framework.
        value = self.identifierOccursCount(self._ui.lineEdit0.text())
        valid_id = (value == 0) or (value == 1 and self._previousIdentifier == self._ui.lineEdit0.text())
        if valid_id:
            self._ui.lineEdit0.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.lineEdit0.setStyleSheet(INVALID_STYLE_SHEET)

        valid_destination = True if len(self._ui.lineEditFileLocation.text()) > 0 else False

        return valid_id and valid_destination

    def getConfig(self):
        """
        Get the current value of the configuration from the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = self._ui.lineEdit0.text()
        config = {}
        config['identifier'] = self._ui.lineEdit0.text()
        config['file'] = self._ui.lineEditFileLocation.text()
        if self._previousLocation:
            config['previous_location'] = os.path.relpath(self._previousLocation, self._workflow_location)
        else:
            config['previous_location'] = ''

        return config

    def setConfig(self, config):
        """
        Set the current value of the configuration for the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = config['identifier']
        self._ui.lineEdit0.setText(config['identifier'])
        if 'file' in config:
            self._ui.lineEditFileLocation.setText(config['file'])
        if 'previous_location' in config:
            self._previousLocation = os.path.join(self._workflow_location, config['previous_location'])

    def _fileChooserClicked(self):
        # Second parameter returned is the filter chosen
        location = QtGui.QFileDialog.getExistingDirectory(self, 'Select Destination for File', self._previousLocation)

        if location:
            self._previousLocation = location
            self._ui.lineEditFileLocation.setText(os.path.relpath(location, self._workflow_location))
