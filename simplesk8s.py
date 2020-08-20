#!/usr/bin/python
# Internal Libraries
import os
import sys
import yaml
import json
import argparse
from multiprocessing import Pool, TimeoutError
from subprocess import DEVNULL, STDOUT, check_call

# External Libraries
from questions.k8s import k8sQuestion, buildKubePrimaryFile
from questions.inventory import inventoryQuestions
from functions.files import createK8sOutputFile, createBoltFile
from functions.eval import evalSocketUptime, activeInventory

# Sets up args
parser = argparse.ArgumentParser(description="Sets up your homelab environment with Bolt")
parser.add_argument(
    "--boltdir", "-b", help="Defines your Boltdir. Defaults to 'Boltdir'.", default="Boltdir",
)
parser.add_argument("--debug", help="Enabled debug log output.", action="store_true", default=False)

# Parses all of your args.
args = parser.parse_args()

try:
    # Definitions
    directory = "{}/data".format(args.boltdir)
    puppetDir = os.getcwd() + "/" + args.boltdir
    inventoryFileName = "{}/inventory.yaml".format(args.boltdir)

    # Create the directory to do everything in.
    try:
        os.makedirs(directory + "/", exist_ok=True)
    except:
        raise

    # Questionnaire time!
    print("We're going to ask you a few questions to get your environment up and going.")

    # Functions
    # K8s Questions
    ktDir, ktEnvFile, ktOS, ktCNI_PROVIDER, etcdClusterHostname, kubePrimary = k8sQuestion(directory=directory)

    # Inventory Questions
    inventoryFile = inventoryQuestions(kubePrimary)

    # Run Docker Builder
    check_call(
        [
            "/usr/bin/docker",
            "run",
            "--rm",
            "-v",
            "{}:/mnt:z".format(ktDir),
            "--env-file",
            ktEnvFile,
            "puppet/kubetool:5.1.0",
        ],
        stdout=DEVNULL,
        stderr=STDOUT,
    )

    # Generate the list of Values, list of Certs, and the filename
    listOfThings, listOfCerts, k8sFile = buildKubePrimaryFile(ktDir, ktOS, ktCNI_PROVIDER, etcdClusterHostname)

    # Create the k8s Output File
    createK8sOutputFile(
        listOfThings,
        listOfCerts,
        "{}/{}/data/kubernetes.yaml".format(os.getcwd(), args.boltdir),
        inventoryFileName,
        inventoryFile,
    )

    # Create Bolt Files
    createBoltFile("bolt.yaml", "{}/bolt.yaml".format(puppetDir))
    createBoltFile("hiera.yaml", "{}/hiera.yaml".format(puppetDir))
    createBoltFile("Puppetfile", "{}/Puppetfile".format(puppetDir))
    createBoltFile(
        "common.yaml",
        "{}/data/common.yaml".format(puppetDir),
        pgp_key_source=listOfThings["kubernetes::docker_key_source"],
        pgp_key_id=listOfThings["kubernetes::docker_key_id"],
    )
    createBoltFile(
        "site-modules/deploy_k8s/plans/deploy.pp", "{}/site-modules/deploy_k8s/plans/deploy.pp".format(puppetDir),
    )
    createBoltFile(
        "site-modules/deploy_k8s/plans/nuke.pp", "{}/site-modules/deploy_k8s/plans/nuke.pp".format(puppetDir),
    )
    createBoltFile(
        "site-modules/prep/manifests/ubuntu.pp", "{}/site-modules/prep/manifests/ubuntu.pp".format(puppetDir),
    )

    # Get a list of all of the hosts in active inventory:
    listOfHosts = activeInventory(args.boltdir)

    # Evaluate if the hosts actually have their SSH sockets open
    print("Evaluating if all hosts are alive:")
    if __name__ == "__main__":
        checkThis = 0
        # Run socket checks against each of the hosts to ensure they are online.
        with Pool(os.cpu_count()) as p:
            checkThis = p.map(evalSocketUptime, listOfHosts)
            if checkThis is False:
                checkThis += 1

        # Evaluate if any of the hosts are offline, and do not continue if so.
        if False in checkThis:
            print(
                "Hosts are not all online. Ensure they are all up and reachable before kicking off the provisioning script!"
            )
            sys.exit(1)
        elif False not in checkThis:
            print("All of the hosts appear up. Let's kick things off!")
        else:
            print("Something went horribly wrong.")
            sys.exit(1)

        # Create the deployment script
        createBoltFile(
            "simplesk8s-deployment.sh.j2",
            "{}/simplesk8s-deployment.sh".format(os.getcwd()),
            fileExecutable=True,
            bolt_project_dir="{}/{}".format(os.getcwd(), args.boltdir),
        )

        print("Run the generated script in your terminal to deploy Kubernetes!")
        print("./simplesk8s-deployment.sh")

        # boltProject = {
        #     "BOLT_PROJECT": "{}/{}".format(os.getcwd(), args.boltdir),
        #     "PATH": os.environ['PATH']
        # }

        # check_call(["/usr/bin/whoami"])

        # # Install the required puppetfile modules
        # check_call(["bolt", "puppetfile", "install", "--debug"], env=boltProject,)
        # # check_call(["/usr/local/bin/bolt", "puppetfile", "install", "--debug"], env=boltProject,)

        # # Run the Bolt Plan
        # check_call(["bolt", "plan", "run", "deploy_k8s::deploy"], env=boltProject)
        # # check_call(["/usr/local/bin/bolt", "plan", "run", "deploy_k8s::deploy"], env=boltProject)
except (KeyboardInterrupt, SystemExit):
    print("\n\nKeyboard Interrupt detected!! Closing SimpleSK8s.")
    sys.exit(1)
