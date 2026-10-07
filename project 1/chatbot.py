"""A small rule-based chatbot with intents, light state and typo tolerance."""

import difflib
import random
import re

YES = r"\b(yes|yeah|yep|sure|absolutely|definitely|ok|okay)\b"
NO = r"\b(no|nope|nah|nay|never|not really)\b"


class Chatbot:
    def __init__(self):
        self.name = None
        self.pending = None  # what the bot is waiting for, e.g. "product_choice"

        # (intent name, user pattern, bot replies). Order = priority.
        self.intents = [
            ("farewell", r"\b(bye|goodbye|see you|quit|exit)\b",
             ["Goodbye, {name}!", "See you later, {name}!", "Take care, {name}!"]),
            ("thanks", r"\b(thanks|thank you|thx)\b",
             ["You're welcome!", "Happy to help, {name}!"]),
            ("greeting", r"\b(hi|hello|hey|greetings)\b",
             ["Hello, {name}!", "Hi there, {name}!", "Greetings, {name}!"]),
            ("pricing", r"\b(price|prices|pricing|cost|costs|how much)\b",
             ["Prices depend on the product. Which one are you asking about?"]),
            ("hours", r"\b(hours|open|opening|closing|close)\b",
             ["We're open Monday to Friday, 9am to 5pm."]),
            ("order_status", r"\b(order|delivery|shipping|tracking)\b",
             ["For order questions, please have your order number ready. What is it?"]),
            ("products", r"\bproducts?\b",
             ["We have a great selection of products! Which one are you interested in?"]),
            ("support", r"\b(help|support|issue|problem|broken|error)\b",
             ["I can help with that. Please describe the issue in more detail."]),
        ]
        self.default_replies = [
            "I'm not sure I understood. You can ask me about products, prices, "
            "opening hours, orders or support.",
            "Sorry, could you rephrase that?",
        ]

        # Words used for typo correction (e.g. "prodcts" -> "products").
        self.vocabulary = sorted({
            word
            for _, pattern, _ in self.intents
            for word in re.findall(r"[a-z]+", re.sub(r"\\[a-z]", " ", pattern))
            if len(word) >= 4
        })

    # ---------- helpers ----------
    @staticmethod
    def _clean(text):
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9'\s]", " ", text)  # drop punctuation
        return re.sub(r"\s+", " ", text).strip()

    def normalize(self, text):
        """Lowercase, strip punctuation and fix small typos."""
        fixed = []
        for word in self._clean(text).split():
            if len(word) >= 4 and word not in self.vocabulary:
                close = difflib.get_close_matches(word, self.vocabulary, n=1, cutoff=0.8)
                word = close[0] if close else word
            fixed.append(word)
        return " ".join(fixed)

    def _say(self, replies):
        return random.choice(replies).format(name=self.name or "friend")

    def _matches(self, intent_name, text):
        for name, pattern, _ in self.intents:
            if name == intent_name:
                return re.search(pattern, text) is not None
        return False

    # ---------- conversation logic ----------
    def _handle_pending(self, text):
        """Interpret the message in light of the bot's last question.
        Returns (intent, reply) or None to fall through to normal matching."""
        state, self.pending = self.pending, None

        if state == "anything_else":
            if re.search(NO, text):
                return "farewell", self._say(["Alright, {name}. Have a great day!"])
            if re.search(YES, text):
                return "yes", "Sure, what else can I help you with?"
            return None

        if state == "product_choice":
            self.pending = "anything_else"
            return "product_detail", (
                f"Good choice! I've noted your interest in '{text}'. "
                "A team member will follow up. Anything else I can help with?"
            )

        if state == "support_details":
            self.pending = "anything_else"
            return "support_detail", (
                "Thanks, I've recorded those details and our support team will "
                "look into it. Anything else I can help with?"
            )
        return None

    def get_response(self, raw_input):
        """Return (intent_name, reply). Does no I/O, so it is easy to test."""
        text = self.normalize(raw_input)
        if not text:
            return "empty", "Please type a message."

        # Goodbyes always work, even in the middle of a question.
        if self.pending and not self._matches("farewell", text):
            result = self._handle_pending(text)
            if result:
                return result
        else:
            self.pending = None

        for name, pattern, replies in self.intents:
            if re.search(pattern, text):
                if name == "products":
                    self.pending = "product_choice"
                elif name == "support":
                    self.pending = "support_details"
                return name, self._say(replies)

        return "default", random.choice(self.default_replies)

    # ---------- I/O ----------
    def greet_user(self):
        raw = input("Bot: Hello! What's your name?\nYou: ").strip()
        # Accept "Ahmed", "my name is Ahmed", "I'm Ahmed"
        raw = re.sub(r"^(my name is|i am|i'm|it's|call me)\s+", "", raw, flags=re.I)
        self.name = raw.title() or None
        print(f"Bot: Nice to meet you, {self.name or 'friend'}! How can I help you today?")

    def run(self):
        try:
            self.greet_user()
            while True:
                intent, reply = self.get_response(input("You: "))
                print("Bot:", reply)
                if intent == "farewell":
                    break
        except (KeyboardInterrupt, EOFError):
            print("\nBot: Goodbye!")


if __name__ == "__main__":
    Chatbot().run()