#!/usr/bin/python3

import yaml
import argparse
import ipaddress as ip
import os
import glob


def generate_config(inventory, output_dir):
    with open(inventory.name, "r", encoding="utf-8") as f:
        input_data = yaml.safe_load(f)

    if input_data["ipv4_base"]:
        ipv4 = ip.IPv4Address(input_data["ipv4_base"])
    else:
        ipv4 = ip.IPv4Address("0.0.0.0")

    if input_data["ipv6_base"]:
        ipv6 = ip.IPv6Address(input_data["ipv6_base"])
    else:
        ipv6 = ip.IPv6Address("::0")

    output_data = []

    for i in input_data["interlink"]:
        output_data.append(
            [
                i["router1"],
                i["iface1"],
                str(ipv4) + "/31",
                str(ipv6) + "/127",
                "to-" + i["router2"] + ":" + i["iface2"],
            ]
        )

        ipv4 = ipv4 + 1
        ipv6 = ipv6 + 1

        output_data.append(
            [
                i["router2"],
                i["iface2"],
                str(ipv4) + "/31",
                str(ipv6) + "/127",
                "to-" + i["router1"] + ":" + i["iface1"],
            ]
        )

        ipv4 = ipv4 + 1
        ipv6 = ipv6 + 1

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        else:
            files = glob.glob(output_dir + "/*.conf")
    else:
        output_dir = os.getcwd()
        files = glob.glob(output_dir + "/*.conf")

    for i in files:
        os.remove(i)

    for i in output_data:
        with open(output_dir + "/" + i[0] + ".conf", "a", encoding="utf-8") as f:
            f.write("set interfaces {} description {}\n".format(i[1], i[4]))
            if input_data["ipv4_base"]:
                f.write(
                    "set interfaces {} unit 0 family inet address {}\n".format(
                        i[1], i[2]
                    )
                )
            if input_data["ipv6_base"]:
                f.write(
                    "set interfaces {} unit 0 family inet6 address {}\n".format(
                        i[1], i[3]
                    )
                )


# execute
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Junos config for P2P links")
    parser.add_argument("inventory", type=open, help="inventory file name")
    parser.add_argument("-o", "--output_dir", type=str, help="output directory")

    args = parser.parse_args()

    generate_config(**vars(args))
else:
    pass
