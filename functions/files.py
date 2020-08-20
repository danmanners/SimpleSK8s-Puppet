import os
import yaml
from jinja2 import FileSystemLoader, Template, Environment

from functions.binary_functions import resource_path

# Jinja Template Information
cwd = os.getcwd()
file_loader = FileSystemLoader("{}/setup/templates".format(resource_path(cwd)))
jinjaLoader = Environment(loader=file_loader)

# Creates the correct and expected K8s Output File for Puppet Bolt usage.
def createK8sOutputFile(listOfThings, listOfCerts, fileName, inventoryFileName, inventoryFile):
    # Adds all of the standard key:values to the top of the file
    with open(fileName, "w") as file:
        yaml.dump(listOfThings, file, explicit_start=True)

    # Appends all of the certificates and keys as key:values to the file.
    with open(fileName, "a") as file:
        certs = yaml.dump(listOfCerts, default_style="|")
        edit1 = certs.replace(": '", ": |\n  ", len(listOfCerts.keys())).replace('"', "")
        file.write(edit1)

    # Creates the Kubernetes Inventory File
    with open(inventoryFileName, "w") as file:
        file.writelines(inventoryFile)


# Creates a file on the filesystem from a Jinja Template file.
def createBoltFile(templateName, outputFileName, fileExecutable=False, **kwargs):
    # Load Template
    template = jinjaLoader.get_template(templateName)
    render = template.render(kwargs)
    directory = outputFileName.rsplit("/", 1)[0]

    # If the directory in question does not exist, create it.
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write Template to Filename
    with open(outputFileName, "w") as file:
        file.writelines(render)

    if fileExecutable == True:
        os.chmod(outputFileName, 0o775)
