# Main logic for PSAbot
import requests
import config


# Status of chatbot
class Stat:
    START = 0
    FUNC = 1
    CHANGE_OS = 2
    CHANGE_LANG = 3
    Q_OR_ERR = 4
    KEYWORD = 5
    METHOD = 6
    CONTINUE = 7
    STOP = 8


class ASSTbot:

    def __init__(self):
        self._status = Stat.START
        self.func = ""  # Function slot
        self.os = ""  # OS system slot
        self.lang = ""  # PL slot
        self.q_or_err = ""  # Question slot

    # Decide the next action of PSAbot
    def next_status(self, prompt):
        # (1). Start chat provide functions
        if self._status == Stat.START:
            self._status = Stat.FUNC
            return self.system_resp()
        # (2). Make user choose function
        elif self._status == Stat.FUNC:
            self.check_intent(prompt)
            print(self._status)
            # (2-1). User request to do other action, like change os, pl
            if self._status != Stat.FUNC:
                print("Hu :o")
                return self.system_resp()
            # (2-2). User chose a function
            else:
                self.set_func(prompt)
                # (2-2-1). 1st time using (Ask for os & pl)
                if self.os == "":
                    self._status = Stat.CHANGE_OS
                    return self.system_resp()
                # (2-2-2). Already collected information, ask for question
                else:
                    self._status = Stat.Q_OR_ERR
                    return self.system_resp()
        # (3). Set OS system
        elif self._status == Stat.CHANGE_OS:
            self.check_intent(prompt)
            # (3-0). User request to do other action, like change os, pl
            if self._status != Stat.CHANGE_OS:
                print("Hu-os :o")
                return self.system_resp()
            self.os = prompt.lower()
            # (3-1). 1st time using, ask for pl immediately
            if self.lang == "":
                self._status = Stat.CHANGE_LANG
            # (3-2). Finish changing OS
            else:
                # (3-2-1). Already chose a function
                if self.func != "":
                    self._status = Stat.Q_OR_ERR
                # (3-2-2). Haven't pick function
                else:
                    self._status = Stat.FUNC
            return self.system_resp()
        # (4). Set PL slot
        elif self._status == Stat.CHANGE_LANG:
            self.check_intent(prompt)
            print(self._status)
            # (4-0). User request to do other action, like change os, pl
            if self._status != Stat.CHANGE_LANG:
                print("Hu-pl :o")
                return self.system_resp()
            self.lang = prompt.lower()
            # (4-1). Already chose a function
            if self.func != "":
                self._status = Stat.Q_OR_ERR
            # (4-2). Haven't pick function
            else:
                self._status = Stat.FUNC
            return self.system_resp()
        # (5). Start analyzing, implement PSAbot method
        elif self._status == Stat.Q_OR_ERR:
            self.q_or_err = prompt
            self._status = Stat.METHOD
            return self.system_resp()
        elif self._status == Stat.METHOD:
            print("Hi :D")
            qkey = self.generate_qkey()
            print(qkey)
            ranks, stack_items = self.search_and_analyze(qkey)
            rank_display = self.get_ranks(ranks, stack_items)
            self._status = Stat.STOP
            return self.system_resp() + "\n" + ranks
        elif self._status == Stat.STOP:
            self._status = Stat.START
            return

    # Detect user's intent
    def check_intent(self, prompt):
        print("Checking intent...")
        if "change os" in prompt.lower():
            self._status = Stat.CHANGE_OS
        elif "change programming language" in prompt.lower() or \
                "change language" in prompt.lower():
            self._status = Stat.CHANGE_LANG
        elif "quit chatting" in prompt.lower():
            self._status = Stat.STOP
        else:
            return

    # System responses
    def system_resp(self):
        if self._status == Stat.FUNC:
            return "Hi! Welcome to PSAbot :D\n" \
                   "These are the services we provide: \n" \
                   "1. Error message solving (Please paste your error message directly)\n" \
                   "2. Guiding QA (Please explain your question.)\n" \
                   "If your question still not fixed, " \
                   "you can discuss with others using the Collaborative Discussion service.\n\n" \
                   "Please enter the service you want."
        elif self._status == Stat.CHANGE_OS:
            return "Which operating system are you using?\n" \
                   "You can change it later by entering 'change OS'"
        elif self._status == Stat.CHANGE_LANG:
            return "Which programming language are you using?\n" \
                   "You can change it later by entering 'change programming language'"
        elif self._status == Stat.Q_OR_ERR:
            if self.func == "guiding_qa":
                return "Please describe your question here: "
            elif self.func == "err_msg":
                return "Please paste your error message here: "
            else:
                return "No such service. Please choose a valid service."
        elif self._status == Stat.METHOD:
            return "Start analyzing..."
        elif self._status == Stat.STOP:
            return "Thanks for waiting!!\n" \
                   "These are the recommended answers for your question: \n"

    # Choose function
    def set_func(self, prompt):
        l_prompt = prompt.lower()
        if "guiding qa" in l_prompt:
            self.func = "guiding_qa"
        elif "error message" in l_prompt:
            self.func = "err_msg"

    # Pre-process user question & generate search keys
    def generate_qkey(self):
        # analyze user question
        response = requests.post(url=config.TOOLBOX_API_HOST + "/api/data_clean",
                                 json={"content": self.q_or_err}).json()
        print(response)
        # generate searching keywords
        qkey = response['token']
        qkey.append(self.os)
        qkey.append(self.lang)
        return qkey

    # Implement main method
    def search_and_analyze(self, qkey):
        # Step 1. Search via Custom JSON Search API
        result_page = requests.post(url=config.TOOLBOX_API_HOST + "/api/search",
                                    json={"keywords": qkey,
                                          "result_num": 10,
                                          "page_num": 0}).json()
        # Step 2. Fetch data
        stack_items = requests.post(url=config.TOOLBOX_API_HOST + "/SO_api/get_items",
                                    json={"urls": result_page['result']}).json()
        # Step 3. block analysis
        response = requests.post(url=config.TOOLBOX_API_HOST + "/api/block_analysis",
                                 json={"items": stack_items['items'], "q": self.q_or_err}).json()
        print(response)
        return response['ranks'], stack_items['items']

    @staticmethod
    def get_ranks(self, ranks, stack_item):
        blocks = []
        for q in stack_item:
            blocks += q['answers']
        block_id = [b['id'] for b in ranks['ranks']]
        display = list(filter(lambda d: d['id'] in block_id, blocks))
        for r in display:
            print("===" + str(r['id']) + "===")
            print(r["content"])
        return display


if __name__ == "__main__":
    bot = ASSTbot()
    print(bot.next_status(""))
    while True:
        user = input("User: ")
        resp = bot.next_status(user)
        print(resp)
        if "start analyzing" in resp.lower():
            resp = bot.next_status("")
            print(resp)
