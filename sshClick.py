#! /usr/bin/env click


from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, NetMikoAuthenticationException
from paramiko.ssh_exception import SSHException
import click
import datetime

# open file and send command with file
def open_send(net_connect, config_file):
    with open(config_file) as c:
        config_lines = c.read().splitlines()

    config_set = net_connect.send_config_set(config_lines)
    return print(config_set)


# send show command with user"s input
def show_command(net_connect, show_cmd):
    cmd_output = net_connect.send_command(show_cmd)
    print(f"The following is the output of {show_cmd}: " + "\n" +
          f"{cmd_output}")
    ans = input(Fore.YELLOW +
                "\nWould you like to save this output to a file? <y/n> " +
                Style.RESET_ALL)
    if ans == "y":
        cmd = show_cmd.replace(" ", "")
        filename = str(device["ip"]) + "_" + cmd + "_" + timestamp
        with open(filename, "w") as f:
            f.write(cmd_output)
        print(f"\n The output has been saved as : {filename}")


def connect(device):
    # try and SSH to the device
    try:
        global net_connect
        net_connect = ConnectHandler(**device)
        print(Fore.CYAN + "\n" + " " * 10 + "----->> Connected to " +
              str(device["ip"]) + " <<-----\n" + Style.RESET_ALL)
        return True
    # if any of the captioned exceptions is raised, print error message
    # continue with rest of the code
    except NetMikoTimeoutException as e:
        print(Fore.RED + "\n" + "~"*15 + str(e) + "~"*15 + "\n" +
              Style.RESET_ALL)
        pass

    except NetMikoAuthenticationException as e:
        print(Fore.RED + "\n" + "~"*15 + str(e) + "~"*15 + "\n" +
              Style.RESET_ALL)
        pass

    except SSHException as e:
        print(Fore.RED + "\n" + "~"*15 + str(e) + "~"*15 + "\n" +
              Style.RESET_ALL)
        pass


def run_if(device):
    if config_file:
        # jumps to open_send() function
        open_send(net_connect, config_file)
        output = net_connect.send_command("wr")
        # saving configurations on device
        print(Fore.CYAN + "-" * 70)
        print(Fore.WHITE + " " * 15 + " Saving on configurations on: " +
              str(device["ip"]))
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)

    if show_cmd:
        #jumps to show_command() function
        show_command(net_connect, show_cmd)



class Device(object):
    def __init__(self, ip=None, device_type=None, username=None, password=None):
        self.ip = ip
        self.device_type = device_type
        self.username = username
        self.password = password


@click.group(invoke_without_command=True)
# file for configuration
@click.option("--config", help="Enter the configuration file name here",
              default=False)
# optional: file for device list
@click.option("--device_list", help="Enter the device list file name here",
              default=False)
# optional: user input show command
@click.option("--cmd", help="Enter the show command here", default=False)
# optional: user input device_type, default = cisco_ios
@click.option("--device_type",
              help="Enter the device type here (default = Cisco IOS)",
              default="cisco_ios")
# user input ip address
@click.option("--ip", help="Enter the device ip address here")
# prompt user for input username
@click.option("--username", help="device username", prompt=True,
              hide_input=False)
# promtp user for input password
@click.option("--password", help="device password", prompt=True,
              hide_input=True)
@click.pass_context
def Project_Net(ctx, config, device_list, cmd, device_type, ip,
        username, password):
    """Welcome! To Network Girl Debi's Click_Netmiko"""

    global device
    global config_file
    global show_cmd

    config_file = config
    show_cmd = cmd

    if ip:
        device = {
            "device_type": device_type,
            "ip": ip,
            "username": username,
            "password": password}

        ctx.obj = device

        print(Fore.MAGENTA + "=" * 70)
        print(Fore.WHITE + " " * 15 + " Connecting to Device: " + ip)
        print(Fore.MAGENTA + "=" * 70 + Style.RESET_ALL)

        if connect(device) is True:
            run_if(device)
            if ctx.invoked_subcommand is None:
                print("No commands has been invoked.")
            else:
                print('Processing command : %s' % ctx.invoked_subcommand)

                if ctx.invoked_subcommand == "Check_OSPF":
                    ctx.invoke(check_ospf)
                if ctx.invoked_subcommand == "Check_EIGRP":
                    ctx.invoke(check_eigrp)

    else:
        with open(device_list) as d:
            for ip in d:
                device = {
                    "device_type": "cisco_ios",
                    "ip": ip,
                    "username": username,
                    "password": password}

                ctx.obj = device

                print(Fore.MAGENTA + "=" * 70)
                print(Fore.WHITE + " " * 15 + " Connecting to Device: " + ip)
                print(Fore.MAGENTA + "=" * 70+ Style.RESET_ALL)

                if connect(device) is True:
                    run_if(device)
                    if ctx.invoked_subcommand is None:
                        print("No commands has been invoked.")
                    else:
                        print('Processing command : %s' % ctx.invoked_subcommand)

                        if ctx.invoked_subcommand == "Check_OSPF":
                            ctx.invoke(check_ospf)
                        if ctx.invoked_subcommand == "Check_EIGRP":
                            ctx.invoke(check_eigrp)

    print("\n" + " " * 10 + Fore.YELLOW + "----->> " +
          Fore.GREEN + "Task Completed!" + Fore.YELLOW +
          " <<-----" + Style.RESET_ALL)
    exit()



if __name__ == "__main__":
    Project_Net()
