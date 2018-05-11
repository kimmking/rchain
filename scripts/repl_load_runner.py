#!/usr/bin/env python3
from pexpect import replwrap
import subprocess
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--grpc-host", dest='grpc_host', default="node0.testnet1.rchain", help="set grpc host")
parser.add_argument("-r", "--repeat", dest='repeat', type=int, default=50, help="set repetition count")
parser.add_argument("-p", "--prompt", dest='prompt', type=str, default="rholang $ ", help="set REPL prompt")
parser.add_argument("-c", "--cpus", dest='cpus', type=int, default=1, help="set docker cpus for repl client node")
parser.add_argument("-m", "--memory", dest='memory', type=int, default=1024, help="set docker memory for repl client node")
parser.add_argument("-n", "--network", dest='network', type=str, default="testnet1.rchain", help="set docker memory for repl client node")
args = parser.parse_args()

result = subprocess.run(["docker", "volume", "create"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
volume_name = result.stdout.decode('ascii').rstrip('\r\n')
print("creating tmp volume: {}".format(volume_name))

# Delete rnode-repl on network if it exists
# result = subprocess.run(["docker", "container", "ls", "--all", "--format", "{{.Names}}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# containers = result.stdout.decode('ascii').splitlines()
# for container in containers:
#   if container.endswith(args.network) and "rnode-repl" in container:
#     print("removing {}".format(container))
#     result = subprocess.run([ "docker", "container", "rm", "-f", container ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Run rnode-repl loader with replwrap
cmd = "sudo docker run --rm -it -v {}:/var/lib/rnode --cpus=.5 --memory=1024m --name rnode-repl.{} --network {} coop.rchain/rnode --grpc-host node0.testnet1.rchain -r".format(volume_name, args.network, args.network)
repl_cmds = ['5', '@"stdout"!("foo")']
conn = replwrap.REPLWrapper(cmd, args.prompt, None)
for i in range(args.repeat):
  for repl_cmd in repl_cmds:
    result = conn.run_command(repl_cmd) 
    print("repetition: {} output: {}".format(i, result))

# Clean up
subprocess.run(["docker", "container", "rm", "-f", "rnode-repl.{}".format(args.network)])
result = subprocess.run(["docker", "volume", "rm", volume_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)