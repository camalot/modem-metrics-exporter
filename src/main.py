import asyncio
import signal
import traceback
from concurrent.futures import ProcessPoolExecutor
from lib.probes.bgw320.BroadbandStatisticsProbe import BroadbandStatisticsProbe
from lib.probes.bgw320.FiberStatusProbe import FiberStatusProbe
from lib.probes.bgw320.HomeNetworkStatsProbe import HomeNetworkStatsProbe
from lib.probes.bgw320.SystemInfoProbe import SystemInfoProbe
from lib.presentations.PrometheusPresentation import PrometheusPresentation
from lib.probes.ProbeFactory import ProbeFactory

from config import ApplicationConfiguration
from dotenv import find_dotenv, load_dotenv
from lib.logging import setup_logging

load_dotenv(find_dotenv())


class ModemProbe:
    def __init__(self):
        self.config = ApplicationConfiguration
        self.logger = setup_logging(config=self.config.logging)

    def sighandler(self, signum, frame):
        self.logger.warning('<SIGTERM received>')
        exit(0)

    def presentation(self):
        try:
            presentation = PrometheusPresentation()
            self.logger.debug('Starting presentation')
            presentation.run()
        except KeyboardInterrupt:
            self.logger.warning('<KeyboardInterrupt received>')
            exit(0)

    def run_probes(self, loop: asyncio.AbstractEventLoop, executor: ProcessPoolExecutor):
        try:
            for modem in self.config.modems:
                self.logger.debug(f'creating probes for {modem.name} : {modem.type}')
                probes = modem.probes
                for probe in probes:
                    try:
                        self.logger.debug(f'creating probe {probe.type}')
                        probe_instance = ProbeFactory.create(modem, probe.type)
                        loop.run_in_executor(executor, probe_instance.run)
                    except Exception as e:
                        self.logger.error(e)
                        self.logger.error(traceback.format_exc())
                        continue

        except KeyboardInterrupt:
            self.logger.warning('<KeyboardInterrupt received>')
            exit(0)


    # def SystemInfoProbe(self):
    #     try:
    #         probe = SystemInfoProbe()
    #         # self.logger.debug('Starting probe')
    #         probe.run()
    #     except KeyboardInterrupt:
    #         self.logger.warning('<KeyboardInterrupt received>')
    #         exit(0)

    # def BroadbandStatisticsProbe(self):
    #     try:
    #         probe = BroadbandStatisticsProbe()
    #         # self.logger.debug('Starting probe')
    #         probe.run()
    #     except KeyboardInterrupt:
    #         self.logger.warning('<KeyboardInterrupt received>')
    #         exit(0)

    # def FiberStatusProbe(self):
    #     try:
    #         probe = FiberStatusProbe()
    #         # self.logger.debug('Starting probe')
    #         probe.run()
    #     except KeyboardInterrupt:
    #         self.logger.warning('<KeyboardInterrupt received>')
    #         exit(0)

    # def HomeNetworkStatsProbe(self):
    #     try:
    #         probe = HomeNetworkStatsProbe()
    #         # self.logger.debug('Starting probe')
    #         probe.run()
    #     except KeyboardInterrupt:
    #         self.logger.warning('<KeyboardInterrupt received>')
    #         exit(0)


if __name__ == '__main__':
    modemprobe = ModemProbe()
    try:
        loop = asyncio.new_event_loop()
        signal.signal(signal.SIGTERM, modemprobe.sighandler)
        try:
            executor = ProcessPoolExecutor()

            loop.run_in_executor(executor, modemprobe.presentation)
            modemprobe.run_probes(loop, executor)

            # loop.run_in_executor(executor, modemprobe.SystemInfoProbe)
            # loop.run_in_executor(executor, modemprobe.BroadbandStatisticsProbe)
            # loop.run_in_executor(executor, modemprobe.FiberStatusProbe)
            # loop.run_in_executor(executor, modemprobe.HomeNetworkStatsProbe)


            loop.run_forever()
        except DeprecationWarning:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()
    except DeprecationWarning:
        pass
