import sys
import random
import hashlib
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QSpinBox, QFileDialog,
    QMessageBox, QCheckBox
)

def luhn_checksum(number_str):
    digits = [int(d) for d in number_str]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] = sum(divmod(digits[i] * 2, 10))
    total = sum(digits)
    return (10 - (total % 10)) % 10

def generate_card_number(iin_prefix):
    iin_str = str(iin_prefix)
    if len(iin_str) < 6 or len(iin_str) > 8:
        raise ValueError("IIN must be 6-8 digits")
    
    card_type, length_range, _ = determine_card_type(iin_prefix)
    
    if isinstance(length_range, int):
        length = length_range
    else:
        length = random.choice(length_range)
    
    remaining_length = length - len(iin_str) - 1
    random_digits = ''.join(str(random.randint(0, 9)) for _ in range(remaining_length))
    partial_number = iin_str + random_digits
    checksum = luhn_checksum(partial_number + '0')
    return partial_number + str(checksum), length

def generate_expiry_date():
    base_year = 2026
    current_year = datetime.now().year
    start_year = max(current_year, base_year)
    expiry_year = start_year + random.randint(1, 10)
    expiry_month = random.randint(1, 12)
    return f"{expiry_month:02d}/{expiry_year % 100:02d}"

def generate_static_cvv(length=3):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def generate_dynamic_cvv(seed, length=3):
    current_time = datetime.now().strftime("%Y%m%d%H")
    hash_input = f"{seed}{current_time}"
    hashed = hashlib.sha256(hash_input.encode()).hexdigest()
    return hashed[:length].upper()

def generate_biometric_token():
    bio_data = ''.join(random.choices('0123456789ABCDEF', k=32))
    return hashlib.sha256(bio_data.encode()).hexdigest()

def generate_did():
    method = random.choice(['ethr', 'key', 'web'])
    identifier = ''.join(random.choices('0123456789abcdef', k=40))
    return f"did:{method}:{identifier}"

def generate_cardholder_name():
    first_names = ["John", "Jane", "Alex", "Emily", "Michael", "Sophia", "David", "Olivia", "James", "Emma"]
    last_names = ["Doe", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_token(card_number):
    token_length = random.randint(16, 19)
    token_prefix = random.choice(['9', '8'])
    remaining = token_length - 1 - 4
    random_part = ''.join(str(random.randint(0, 9)) for _ in range(remaining))
    return token_prefix + random_part + card_number[-4:]

def generate_3ds_code():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))

def determine_card_type(iin_prefix):
    iin_str = str(iin_prefix)
    if iin_str.startswith('4'):
        return 'Visa', [16, 19], 3
    elif iin_str.startswith('5') or iin_str.startswith('2'):
        return 'Mastercard', 16, 3
    elif iin_str.startswith('34') or iin_str.startswith('37'):
        return 'American Express', 15, 4
    elif iin_str.startswith('6'):
        return 'Discover', [16, 19], 3
    elif iin_str.startswith('62') or iin_str.startswith('81'):
        return 'UnionPay', [16, 19], 3
    elif iin_str.startswith('7'):
        return 'Crypto/Stablecoin', [16, 19], 3
    else:
        return 'Unknown', 16, 3

def generate_cards(iin_prefix, count, include_token=False, include_3ds=False, include_biometric=False, include_dynamic_cvv=False, include_did=False):
    card_type, length_range, default_cvv = determine_card_type(iin_prefix)
    cards = []
    for _ in range(count):
        card_number, actual_length = generate_card_number(iin_prefix)
        expiry = generate_expiry_date()
        cvv_seed = random.randint(100000, 999999)
        cvv_length = default_cvv
        cvv = generate_dynamic_cvv(cvv_seed, cvv_length) if include_dynamic_cvv else generate_static_cvv(cvv_length)
        name = generate_cardholder_name()
        card = {
            'type': card_type,
            'number': card_number,
            'length': actual_length,
            'expiry': expiry,
            'cvv': cvv,
            'name': name
        }
        if include_dynamic_cvv:
            card['cvv_note'] = f"Dynamic (seed: {cvv_seed}, changes hourly)"
        if include_token:
            card['token'] = generate_token(card_number)
        if include_3ds:
            card['3ds_code'] = generate_3ds_code()
        if include_biometric:
            card['biometric_token'] = generate_biometric_token()
        if include_did:
            card['did'] = generate_did()
        cards.append(card)
    return cards

class CardGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Card Generator 2030")
        self.resize(720, 640)
        self.layout = QVBoxLayout()

        self.iin_label = QLabel("IIN (6–8 digits):")
        self.iin_input = QLineEdit()
        self.iin_input.setPlaceholderText("Example: 411111")
        self.layout.addWidget(self.iin_label)
        self.layout.addWidget(self.iin_input)

        self.count_label = QLabel("Number of cards:")
        self.count_input = QSpinBox()
        self.count_input.setMinimum(1)
        self.count_input.setMaximum(200)
        self.count_input.setValue(10)
        self.layout.addWidget(self.count_label)
        self.layout.addWidget(self.count_input)

        self.token_cb = QCheckBox("Add tokens (digital wallets / stablecoins)")
        self.threeds_cb = QCheckBox("Add 3DS codes")
        self.bio_cb = QCheckBox("Add biometric tokens")
        self.dyn_cvv_cb = QCheckBox("Add dynamic CVV")
        self.did_cb = QCheckBox("Add DID (decentralized identity)")

        for cb in [self.token_cb, self.threeds_cb, self.bio_cb, self.dyn_cvv_cb, self.did_cb]:
            self.layout.addWidget(cb)

        self.generate_btn = QPushButton("Generate Cards")
        self.generate_btn.clicked.connect(self.generate)
        self.layout.addWidget(self.generate_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.save_btn = QPushButton("Save to File")
        self.save_btn.clicked.connect(self.save_result)
        self.layout.addWidget(self.save_btn)

        self.setLayout(self.layout)

    def generate(self):
        try:
            iin_text = self.iin_input.text().strip()
            if not iin_text:
                QMessageBox.warning(self, "Error", "Please enter IIN")
                return
            if not iin_text.isdigit():
                QMessageBox.warning(self, "Error", "IIN must contain only digits")
                return
            iin = int(iin_text)
            if len(str(iin)) < 6 or len(str(iin)) > 8:
                QMessageBox.warning(self, "Error", "IIN must be between 6 and 8 digits")
                return

            count = self.count_input.value()

            cards = generate_cards(
                iin, count,
                include_token=self.token_cb.isChecked(),
                include_3ds=self.threeds_cb.isChecked(),
                include_biometric=self.bio_cb.isChecked(),
                include_dynamic_cvv=self.dyn_cvv_cb.isChecked(),
                include_did=self.did_cb.isChecked()
            )

            out = ""
            for idx, card in enumerate(cards, 1):
                out += f"Card {idx}\n"
                out += f"Type: {card['type']}\n"
                out += f"Number: {card['number']}  (length: {card['length']})\n"
                out += f"Expiry: {card['expiry']}\n"
                out += f"CVV: {card['cvv']}"
                if 'cvv_note' in card:
                    out += f" ({card['cvv_note']})"
                out += "\n"
                out += f"Name: {card['name']}\n"
                if 'token' in card:
                    out += f"Token: {card['token']}\n"
                if '3ds_code' in card:
                    out += f"3DS Code: {card['3ds_code']}\n"
                if 'biometric_token' in card:
                    out += f"Biometric Token: {card['biometric_token']}\n"
                if 'did' in card:
                    out += f"DID: {card['did']}\n"
                out += "─" * 60 + "\n\n"

            self.output.setPlainText(out)

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{type(e).__name__}\n{str(e)}")

    def save_result(self):
        text = self.output.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Nothing to save", "Generate some cards first")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Text Files (*.txt);;All Files (*.*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "Success", "File saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))

def main():
    app = QApplication(sys.argv)
    window = CardGeneratorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
