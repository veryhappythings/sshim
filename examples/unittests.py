import unittest
import paramiko

import sshim

class SSHimClient(object):
    def __init__(self, sshim_server):
        self.server = sshim_server
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.server.address, port=self.server.port)
        channel = self.client.invoke_shell()
        self.fileobj = channel.makefile('rw')
        self.log = []

    def write(self, input):
        self.fileobj.write(input + '\n')
        log_entry = self.fileobj.readline()
        self.log.append(log_entry)
        return log_entry

    def read(self):
        log_entry = self.fileobj.readline()
        self.log.append(log_entry)
        return log_entry


def device(script):
    script.write("Enter password:")
    script.expect(r'(?P<password>.*)')
    if script['password'] == 'password':
        script.writeline('Welcome to the test device.')
        while script['command'] != 'quit':
            script.write("> ")
            script.expect(r'(?P<command>.*)')
            script.writeline(script['command'])
    else:
        script.writeline("Incorrect password.")


class TestUsingSSHim(unittest.TestCase):
    def test_correct_password(self):
        with sshim.Server(device, port=3000) as server:
            client = SSHimClient(server)
            client.write('password')
            self.assertEqual(client.read(), 'Welcome to the test device.\r\n')
            client.write("example_command")
            self.assertEqual(client.read(), 'example_command\r\n')
            client.write("another_command")
            self.assertEqual(client.read(), 'another_command\r\n')
            client.write("quit")

    def test_incorrect_password(self):
        with sshim.Server(device, port=3000) as server:
            client = SSHimClient(server)
            client.write('wrong password')
            self.assertEqual(client.read(), 'Incorrect password.\r\n')
