# Things to look into

Here's a list of things to either look into or add to the project:

- [ ] Look into the Click library (PalletsProjects)
- [x] Use sockets to evaluate if TCP/22 is open on the remote hosts before executing Puppet Bolt
- [ ] Add subprocesses to evaluate if Docker and Puppet Bolt are installed
- [ ] Add a subprocess to run the Puppet Bolt Plans
- [ ] Add arguments for various tasks and variable entry to avoid the requirements for questions.
- [ ] Actually enable verbose output from the debug flag for argparse.
- [ ] Ensure that the plans are run with BOLT_PROJECT='/mnt/c/Users/danie/code/SimpleSK8s/${args.boltdir}' at the front; else they will fail on WSL2
- [ ] Make it more clear that the hostname for your primary K8s node is important.
