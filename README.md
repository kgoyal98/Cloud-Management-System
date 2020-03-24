# Cloud-Management-System
This is a cloud management system built over the libvirt API. This is an autoscaling socket based client-server application in which servers perform some computation for each request and send suitable responses back to the client. 
The application **elastically scales** the server application by spawning more virtual machines in response to varying load and it also accounts for **server failures**.
## Getting Started



### Prerequisites

Requirements for the client is in client/requirements.txt. The code is developed in Python 3.6.9


### Installing


- Configure KVM using [this](https://www.linuxtechi.com/install-configure-kvm-ubuntu-18-04-server/) if using QEMU/KVM virtual machines. QEMU/KVM needs special hardware support. If you don't have VT-X support, use Xen, VMWare workstation or other hypervisors.
- Setup python dependencies
```
pip3 install -r client/requirements.txt 
```
- Install and open virt-manager
- Create and setup a new virtual machine using virt-manager (I used QEMU/KVM Ubuntu Server 18.04.4 for the VMs)
- Transfer the server files to the VM through SSH or git
- Transfer configure the path of the server.py file in rc.local file and transfer it to /etc/ folder 

```
cd $SERVER
sudo cp rc.local /etc/
```

- Create multiple copies of the VM just created either by following the previous steps again or cloning the initial VM. If cloning, don't forget to change the name of machine in /etc/hostname and machine id in /etc/machine-id. Reason [here](https://jaylacroix.com/fixing-ubuntu-18-04-virtual-machines-that-fight-over-the-same-ip-address/)


## Running the application

The application finds the collision strings with same hash as the client sends. You can change the functionality by changing the function in server code and the requests in client code. In server.py, add the function that you want the server to compute in the file and pass it to the Program object initialisation 

- Shut down all the VMs
- Run client.py file on client

```
python3 client.py
```
- The inter request time (in seconds) can be configured any number of times by entering it in the client console to adjust load
- When done, entering ```exit``` in the console will shut down all the running VMs. It can also be done via virt-manager

The log file for client will be created in the current directory while running the command
