import argparse
import json
from datetime import datetime

# Analyse for a Dos Attack


class DosAnalyzer:
    def __init__(self, dataset_path) -> None:
        self.dataset_path: str = dataset_path
        self.dataset: list = self.read_json(self.dataset_path)
        self.protocol: dict = None
        self.average_session_length: float = None
        self.ip_outside_worktime: dict = None
        self.verbose: bool = False
        self.work_start: datetime = datetime(1970, 1, 5, 3, 23, 53)
        self.work_stop: datetime = datetime(1970, 1, 5, 3, 24, 53)

    # Reads the dataset file

    def read_json(self, jsonfile: str) -> list:
        # Open the file
        with open(jsonfile, "r") as file:
            # Load the file
            dataset: list = json.load(file)
        return dataset

    # Check what protocols the hosts use
    def protocol_by_ip(self) -> dict:
        protocol: dict = {}

        # extract data from the dataset
        for data in self.dataset:
            source_ip: str = data['_source']['layers']['ip']['ip.src']
            frame_protocol: str = data['_source']['layers']['frame']['frame.protocols']

            # Make sure it only uses the last value in the list
            frame_protocol: str = frame_protocol.split(":")[-1]

            # Make sure the list "protocols" doesn't have any double protocols by a source_ip
            if source_ip in protocol and frame_protocol not in protocol[source_ip]:
                protocol[source_ip].append(frame_protocol)
            else:
                protocol[source_ip]: list = [frame_protocol]

        self.protocol: dict = protocol

    # Show the used protocols sorted by ip
    def show_protocol_by_ip(self) -> None:
        for ip, protocols in self.protocol.items():
            protocol_by_ip: str = ", ".join(protocols)
            # print the ip and the corresponding protocols
            print(f"The ip {ip} has used the protocols: {protocol_by_ip}")

    # Calculate the average communication-length between the hosts and server

    def average_communication_length(self) -> list:
        session_length: list = []

        # Collect necessary data from the dataset
        for data in self.dataset:
            ack: str = data['_source']['layers']['tcp']['tcp.flags_tree']['tcp.flags.ack']
            fin: str = data['_source']['layers']['tcp']['tcp.flags_tree']['tcp.flags.fin']
            time_relative: int = abs(
                float(data['_source']['layers']['frame']['frame.time_relative']))

            # Only add the times of the last packet in a communication-session
            if ack == "1" and fin == "1":
                session_length.append(time_relative)
        # Sum of all times
        sum_session_length: int = sum(session_length)
        # Total amount of times
        len_session_length: int = len(session_length)
        # average session-time in seconds
        average_session_length: float = sum_session_length / len_session_length

        self.average_session_length: float = average_session_length

    # Show the average communication length
    def show_average_communication_length(self) -> None:
        # Print the average session-time rounded by 2 decimals
        print(
            f"Average session time between server and hosts is: {self.average_session_length:.2f} seconds")

    # Check if there are any communication-sessions outside worktime

    def worktime(self) -> dict:
        times_of_connections: dict = {}
        # Work start time

        for data in self.dataset:
            source_ip: str = data['_source']['layers']['ip']['ip.src']
            frametime: float = float(
                data['_source']['layers']['frame']['frame.time_epoch'])

            # Save the frametime in the dictionary times_of_connections belonging to the source_ip of the frametime
            # If source_ip not in times_of_connections, add it to times_of_connections
            if source_ip not in times_of_connections:
                times_of_connections[source_ip] = [
                    datetime.fromtimestamp(frametime)]
            # If source_ip in times_of_connections, add the time to the list from the source_ip
            else:
                times_of_connections[source_ip].append(
                    datetime.fromtimestamp(frametime))

        for ip, time_list in times_of_connections.items():
            # Save packages that are outside the worktime
            marked_frames: list = []
            ips_to_delete: list = []

            # Check for every time if the time is outside worktime
            for time in time_list:
                if time > self.work_stop or time < self.work_start:
                    marked_frames.append(str(time))

            # Add the ip's that has no connections outside worktime to the list ip's_to_delete
            if not marked_frames:
                ips_to_delete.append(ip)

        # Delete the ip's in ip's_to_delete from the dictionary times_of_connections
        for ip in ips_to_delete:
            times_of_connections.pop(ip)

        self.ip_outside_worktime: dict = times_of_connections

    # Show the connections outside worktime ordered by ip

    def show_worktime(self) -> None:
        for ip, marked_frames in self.ip_outside_worktime.items():

            # Extra option to show all the times by ip
            if self.verbose:
                print(
                    f"The ip {ip} has connected to the server outside worktime at {', '.join(str(frame) for frame in marked_frames)}")

            # Count all times from every ip and show them
            else:
                print(
                    f"The ip {ip} has {len(marked_frames)} times connected to the server outside the worktime")

        # Show a hint to use the verbose option
        if not self.verbose:
            print(
                '    Add argument -V to view all times that the ip connected to the server outside the worktime')


def main() -> None:

    # Command Line Interface
    parser = argparse.ArgumentParser("JSON Dataset Analyse")
    parser.add_argument("json_file_path", metavar="filename",
                        type=str, help="File location of the json file")
    parser.add_argument("-P", "--protocols_used", action="store_true",
                        help="Search in the dataset for used protocols by ip's")
    parser.add_argument("-C", "--communication_length", action="store_true",
                        help="Search in the dataset for the average Communication_length")
    parser.add_argument("-W", "--worktime_analysis", action="store_true",
                        help="Search for communications outside worktime")
    parser.add_argument("-V", "--verbose",
                        action="store_true", help="Verbose output")
    parser.add_argument("-A", "--all", action="store_true",
                        help="Select every method of the program")
    args = parser.parse_args()

    dos_analyzer = DosAnalyzer(args.json_file_path)

    print('########################################################################################################################################')

    # Execute the function protocols_used if the argument is -P or -A
    if args.protocols_used or args.all:
        print()
        dos_analyzer.protocol_by_ip()
        dos_analyzer.show_protocol_by_ip()
        print()

    # Execute the function protocols_used if the argument is -C or -A
    if args.communication_length or args.all:
        print()
        dos_analyzer.average_communication_length()
        dos_analyzer.show_average_communication_length()
        print()

    # Execute the function protocols_used if the argument is -W or -A
    if args.worktime_analysis or args.all:
        print()
        if args.verbose:
            dos_analyzer.verbose = True
        dos_analyzer.worktime()
        dos_analyzer.show_worktime()
        print()

    print('########################################################################################################################################')


if __name__ == "__main__":
    main()
