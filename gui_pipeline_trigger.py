import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit,
    QCheckBox, QPushButton, QMessageBox, QTabWidget, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)

class PipelineTriggerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pipeline Trigger GUI")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Tab widget for stages
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Add Build Parameters Tab
        self.build_parameters_tab = self.create_build_parameters_tab()
        self.tabs.addTab(self.build_parameters_tab, "Pipeline Configurations")

        # Add tabs for each stage
        self.kit4u_tab = self.create_stage_tab("KIT4U")
        self.dpcp_tab = self.create_stage_tab("DPCP")
        self.pmda_tab = self.create_stage_tab("PMDA")
        self.analyzer_tab = self.create_stage_tab("Analyzer")
        self.matlab_tab = self.create_stage_tab("MATLAB Simulations")

        self.tabs.addTab(self.kit4u_tab, "KIT4U")
        self.tabs.addTab(self.dpcp_tab, "DPCP")
        self.tabs.addTab(self.pmda_tab, "PMDA")
        self.tabs.addTab(self.analyzer_tab, "Analyzer")
        self.tabs.addTab(self.matlab_tab, "MATLAB Simulations")

        # Submit button
        self.submit_button = QPushButton("Trigger All Builds")
        self.submit_button.clicked.connect(self.trigger_pipeline)
        self.layout.addWidget(self.submit_button)

        # Set layout
        self.setCentralWidget(self.central_widget)

    def create_build_parameters_tab(self):
        """Create the Build Parameters tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Build Name input
        self.build_name_input = self.create_input_field("Build Name:", "DefaultBuildName", layout)

        # Azure DevOps configuration inputs
        self.user_input = self.create_input_field("Azure DevOps User:", "", layout)
        self.password_input = self.create_input_field("Azure DevOps Password/Token:", "", layout, is_password=True)
        self.azure_url_input = self.create_input_field("Azure DevOps URL:", "https://dev.azure.com", layout)
        self.azure_project_input = self.create_input_field("Azure DevOps Project:", "", layout)
        self.pipeline_id_input = self.create_input_field("Pipeline ID:", "", layout)
        self.branch_input = self.create_input_field("Branch:", "main", layout)

        # Checkboxes for enabling/disabling stages
        self.run_kit4u_checkbox = self.create_checkbox("Enable KIT4U Stage", layout)
        self.run_dpcp_checkbox = self.create_checkbox("Enable DPCP Stage", layout, default=True)
        self.run_pmda_checkbox = self.create_checkbox("Enable PMDA Stage", layout, default=True)
        self.run_analyzer_checkbox = self.create_checkbox("Enable Analyzer Stage", layout, default=True)
        self.run_matlab_checkbox = self.create_checkbox("Enable MATLAB Simulations Stage", layout)

        return tab

    def create_stage_tab(self, stage_name):
        """Create a tab for a stage with two sub-tabs: Parameters and Variables."""
        stage_tab = QWidget()
        stage_layout = QVBoxLayout(stage_tab)

        # Sub-tabs for parameters and variables
        sub_tabs = QTabWidget()
        stage_layout.addWidget(sub_tabs)

        # Parameters tab
        parameters_tab = QWidget()
        parameters_layout = QVBoxLayout(parameters_tab)
        self.add_parameters_fields(stage_name, parameters_layout)
        parameters_tab.setLayout(parameters_layout)  # Ensure layout is set
        sub_tabs.addTab(parameters_tab, "Parameters")

        if stage_name == "DPCP" or stage_name == "KIT4U" or stage_name == "MATLAB Simulations":
            variables_tab = QWidget()
            variables_layout = QVBoxLayout(variables_tab)
            self.add_variables_table(variables_layout)
            variables_tab.setLayout(variables_layout)  # Ensure layout is set
            sub_tabs.addTab(variables_tab, "Running VARIABLES")
           
        if stage_name == "DPCP":
            variables_tab = QWidget()
            variables_layout = QVBoxLayout(variables_tab)
            self.add_variables_table(variables_layout)
            variables_tab.setLayout(variables_layout)  # Ensure layout is set
            sub_tabs.addTab(variables_tab, "OFP_CFP")
            variables_tab = QWidget()
            variables_layout = QVBoxLayout(variables_tab)
            self.add_variables_table(variables_layout)
            variables_tab.setLayout(variables_layout)  # Ensure layout is set
            sub_tabs.addTab(variables_tab, "CFG_VER")



        stage_tab.setLayout(stage_layout)  # Ensure layout is set
        return stage_tab

    def create_input_field(self, label_text, default_value, layout, is_password=False):
        """Create a labeled input field."""
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default_value)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def create_checkbox(self, label_text, layout, default=False):
        """Create a checkbox."""
        checkbox = QCheckBox(label_text)
        checkbox.setChecked(default)
        layout.addWidget(checkbox)
        return checkbox

    def add_variables_table(self, layout):
        """Add a table for defining variables."""
        # Create the table
        table = QTableWidget()
        table.setColumnCount(2)  # Two columns: Variable Name and Value
        table.setRowCount(6)  # One row for variable names, and 5 rows for values


        # Set the first row as the variable names (editable)
        table.setVerticalHeaderLabels(["Variable Names"] + [f"Value {i}" for i in range(1, 6)])
        for col in range(2):  # Make the first row editable for variable names
            item = QTableWidgetItem()
            table.setItem(0, col, item)

        # Make the subsequent rows editable for values
        for row in range(1, 6):  # Rows for values
            for col in range(2):
                item = QTableWidgetItem()
                table.setItem(row, col, item)

        # Add the table to the layout
        layout.addWidget(table)

    def add_parameters_fields(self, stage_name, layout):
        """Add input fields or a table for parameters specific to the stage."""
        if stage_name == "KIT4U":
            self.kit4u_path_input = self.create_input_field("KIT4U Path:", "", layout)
        elif stage_name == "DPCP":
            self.image_name_input = self.create_input_field("DPCP Image Name:", "", layout)
            self.image_tag_input = self.create_input_field("DPCP Image Tag:", "latest", layout)
            self.docker_registry_input = self.create_input_field("Docker Registry:", "", layout)
        elif stage_name == "PMDA":
            self.pmda_cli_path_input = self.create_input_field("PMDA CLI Path:", "", layout)
            self.pmda_blue_route_input = self.create_checkbox("PMDA Make Blue Route:", layout)
            self.pmda_freq_input = self.create_input_field("PMDA Frequency:", "120", layout)
            self.pmda_lines_input = self.create_input_field("PMDA Lines:", "-1", layout)
        elif stage_name == "Analyzer":
            self.analyzer_path_input = self.create_input_field("Analyzer Path:", "", layout)
        elif stage_name == "MATLAB Simulations":
            # Create a single-column table for MATLAB simulation paths
            self.matlab_table = QTableWidget()
            self.matlab_table.setColumnCount(1)  # Single column for simulation paths
            self.matlab_table.setRowCount(5)  # Default to 5 rows
            self.matlab_table.setHorizontalHeaderLabels(["Simulation Path"])
            self.matlab_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # Add the table to the layout
            layout.addWidget(self.matlab_table)

            # Add a button to add rows dynamically
            add_row_button = QPushButton("Add Row")
            add_row_button.clicked.connect(self.add_row_to_matlab_table)
            layout.addWidget(add_row_button)

    def add_row_to_matlab_table(self):
        """Add a new row to the MATLAB Simulations table."""
        current_row_count = self.matlab_table.rowCount()
        self.matlab_table.insertRow(current_row_count)

    def trigger_pipeline(self):
        """Collect inputs and send API requests for all builds."""
        # Collect parameters for Azure DevOps and pipeline configuration
        azure_devops_config = {
            "user": self.user_input.text(),
            "password": self.password_input.text(),
            "azure_url": self.azure_url_input.text(),
            "project": self.azure_project_input.text(),
            "pipeline_id": self.pipeline_id_input.text(),
            "branch": self.branch_input.text(),
        }

        # Collect parameters for each stage
        parameters = {
            "buildName": self.build_name_input.text(),
            "runKIT4U": self.run_kit4u_checkbox.isChecked(),
            "runDPCP": self.run_dpcp_checkbox.isChecked(),
            "runPMDA": self.run_pmda_checkbox.isChecked(),
            "runAnalyzer": self.run_analyzer_checkbox.isChecked(),
            "runMatlabSimulations": self.run_matlab_checkbox.isChecked(),
        }

        # Send API request
        try:
            api_url = f"{azure_devops_config['azure_url']}/{azure_devops_config['project']}/_apis/pipelines/{azure_devops_config['pipeline_id']}/runs?api-version=6.0-preview.1"
            headers = {
                "Content-Type": "application/json",
            }
            auth = (azure_devops_config["user"], azure_devops_config["password"])
            payload = {
                "resources": {
                    "repositories": {
                        "self": {
                            "refName": f"refs/heads/{azure_devops_config['branch']}"
                        }
                    }
                },
                "templateParameters": parameters,
            }
            response = requests.post(api_url, json=payload, headers=headers, auth=auth)
            response.raise_for_status()

            # Show success message
            QMessageBox.information(self, "Success", f"Pipeline triggered successfully!\nResponse: {response.json()}")
        except requests.exceptions.RequestException as e:
            # Show error message
            QMessageBox.critical(self, "Error", f"Failed to trigger pipeline:\n{str(e)}")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PipelineTriggerApp()
    window.show()
    sys.exit(app.exec_())