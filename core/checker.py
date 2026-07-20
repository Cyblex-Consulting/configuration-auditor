import re


class Checker:
    """Base class for every check, regardless of vendor.

    A check receives a `device` (a vendor-specific subclass of core.device.Device)
    and reads configuration through it. This class stays vendor-agnostic; all
    vendor knowledge lives in the Device subclass and in the checks themselves.
    """

    def __init__(self, device, display, verbose=False):
        self.device = device
        # Backward-compatible alias: existing FortiGate checks reference
        # `self.firewall`. New checks should prefer `self.device`.
        self.firewall = device
        self.display = display
        self.verbose = verbose
        self.message = None
        self.manual_entry = False
        self.auto = True
        self.enabled = True
        self.levels = None
        self.benchmark_author = None
        self.question_context = None
        self.question = None
        self.answer = None

    def __lt__(self, other):
        return self.id < other.id

    def is_valid(self):

        if self.id is None:
            print(f'[!] Error in {self.__class__.__name__}: Check id is not defined')
            return False
        if self.title is None:
            print(f'[!] Error in {self.__class__.__name__}: Check title is not defined')
            return False
        if self.levels is None or len(self.levels) == 0:
            print(f'[!] Error in {self.__class__.__name__}: Levels are not defined')
            return False
        if self.benchmark_author is None or len(self.benchmark_author) == 0:
            print(f'[!] Error in {self.__class__.__name__}: Benchmark author is not defined')
            return False

        return True

    def is_level_applicable(self, levels):
        # Checks if the level asked by the operator is applicable to this check
        for level in levels:
            if int(level) in self.levels:
                return True
        return False

    def print_verbose(self, content):
        print(f'\t| {content}')

    def restore_from_cache(self, cached_result):
        self.result = cached_result["result"]
        self.message = cached_result["message"]
        self.question = cached_result["question"]
        self.question_context = cached_result["question_context"]
        self.answer = cached_result["answer"]
        print(f'[{self.get_id()}] {self.title}', end='')
        print(f' : {self.result}')
        if self.verbose and self.question_context is not None:
            self.display.show(self.question_context)
        if self.verbose and self.question is not None:
            self.display.show(self.question)
        if self.verbose and self.answer is not None:
            self.display.show(self.answer)
        if self.verbose and self.message is not None:
            self.display.show(self.message)

    def skip(self):
        print(f'[{self.get_id()}] {self.title} : SKIP')
        self.result = 'SKIP'

    def run(self):

        if not self.is_valid():
            return False

        print(f'[{self.get_id()}] {self.title}', end='')
        self.success = self.do_check()

        if self.success is None:
            self.result = 'SKIP'
        else:
            if self.success:
                self.result = 'PASS'
            else:
                self.result = 'FAIL'

        if self.manual_entry:
            if self.verbose and self.message is not None:
                self.display.show(self.message)

            print(f'[{self.get_id()}] {self.title} : {self.result}')
        else:
            print(f' : {self.result}')
            if self.verbose and self.message is not None:
                self.display.show(self.message)

    # Handle manual questions
    def set_question_context(self, question_context):
        self.question_context = [question_context]

    def add_question_context(self, question_context):
        if self.question_context is None:
            self.question_context = []
        self.question_context.append(question_context)

    def ask(self, question):
        self.manual_entry = True
        self.question = question
        self.answer = self.display.ask(self.question_context, question)
        return self.answer

    def ask_if_correct(self, question="Is it correct?"):

        answer = self.ask(question + " ([Y]es/[n]o/[s]kip)")

        if answer == 'n' or answer == 'N':
            self.set_message("Manually set to not compliant")
            return False
        if answer == 's' or answer == 'S':
            self.set_message("Skipped")
            return None
        else:
            self.set_message("Manually set to compliant")
            return True

    # Handle result display
    def set_message(self, message):
        self.message = [message]

    def add_message(self, message):
        if self.message is None:
            self.message = []
        self.message.append(message)

    # Internal helpers
    def get_result(self):
        return self.result

    def get_title(self):
        return self.title

    def get_id(self):
        return f'{self.benchmark_author}-{self.id}'

    def get_log(self):
        log = ""
        if self.question is not None:
            if self.question_context is not None:
                if isinstance(self.question_context, list):
                    log += "\n".join(self.question_context)
                else:
                    log += self.question_context
                log += "\n"
            if self.question is not None:
                log += self.question
                log += "\n"
            if self.answer is not None:
                log += self.answer
                log += "\n"
            if self.message is not None:
                log += "\n".join(self.message)
        elif self.message is not None:
            log += "\n".join(self.message)
        return log

    # Helper function to get the correct config block in the config dict
    def get_config(self, chapter=None):
        return self.device.get_config(chapter)

    # Helper function to check if param is an IP
    def is_ip(self, param):
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", param):
            return True
        else:
            return False

    # Helper function to check if param is a valid hostname or FQDN
    def is_fqdn(self, param):
        if re.match(r"^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$", param):
            return True
        else:
            return False

    # Helper to return WAN interfaces
    def get_wan_interfaces(self):
        return self.device.get_wan_interfaces()
