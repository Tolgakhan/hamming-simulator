import tkinter as tk
from tkinter import messagebox, ttk
import random

# --- Hamming Code Fonksiyonlari ---
def calculate_hamming_code(data_bits):
    m = len(data_bits)
    r = 0
    while (2 ** r) < (m + r + 1):
        r += 1

    total_length = m + r + 1  # +1 for SEC-DED overall parity
    hamming_code = ['0'] * total_length
    j = 0

    for i in range(1, total_length):
        if (i & (i - 1)) != 0:
            hamming_code[i] = data_bits[j]
            j += 1

    for i in range(r):
        parity_pos = 2 ** i
        parity = 0
        for j in range(1, total_length):
            if j & parity_pos:
                parity ^= int(hamming_code[j])
        hamming_code[parity_pos] = str(parity)

    overall_parity = sum(int(bit) for bit in hamming_code[1:]) % 2
    hamming_code[0] = str(overall_parity)

    return ''.join(hamming_code)

def bit_flip(bit_string, index):
    bit_list = list(bit_string)
    bit_list[index] = '1' if bit_list[index] == '0' else '0'
    return ''.join(bit_list)

def detect_and_correct(hamming_code):
    n = len(hamming_code)
    r = 0
    while (2 ** r) < n:
        r += 1

    error_pos = 0
    for i in range(r):
        parity_pos = 2 ** i
        parity = 0
        for j in range(1, n):
            if j & parity_pos:
                parity ^= int(hamming_code[j])
        if parity != int(hamming_code[parity_pos]):
            error_pos += parity_pos

    expected_parity = sum(int(hamming_code[i]) for i in range(1, n)) % 2
    if expected_parity != int(hamming_code[0]):
        if error_pos == 0:
            return "Çift hata tespit edildi. Düzeltilemez.", hamming_code
        else:
            corrected = bit_flip(hamming_code, error_pos)
            return f"Tek bit hatası tespit edildi ve {error_pos}. pozisyonda düzeltildi.", corrected
    else:
        if error_pos == 0:
            return "Hata bulunamadı.", hamming_code
        else:
            corrected = bit_flip(hamming_code, error_pos)
            return f"Tek bit hatası tespit edildi ve {error_pos}. pozisyonda düzeltildi.", corrected

# --- GUI Sınıfı ---
class HammingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamming SEC-DED Simülatörü")
        self.memory = []
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Veri (8/16/32 bit, sadece 0 ve 1):").pack()

        self.data_entry = tk.Entry(self.root, width=40)
        self.data_entry.pack()

        tk.Button(self.root, text="Hamming Kodu Hesapla ve Belleğe Yaz", command=self.encode_and_store).pack(pady=5)

        columns = ("no", "data", "hamming", "status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        self.tree.heading("no", text="No")
        self.tree.heading("data", text="Veri")
        self.tree.heading("hamming", text="Hamming Kodu")
        self.tree.heading("status", text="Durum")

        self.tree.column("no", width=40, anchor="center")
        self.tree.column("data", width=180, anchor="center")
        self.tree.column("hamming", width=250, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        self.tree.pack(pady=10)

        tk.Button(self.root, text="Seçilen Veride Hata Oluştur", command=self.introduce_error).pack(pady=3)
        tk.Button(self.root, text="Hata Tespit Et ve Düzelt", command=self.correct_error).pack(pady=3)

    def encode_and_store(self):
        data = self.data_entry.get().strip()
        if not all(c in '01' for c in data):
            messagebox.showerror("Hata", "Veri sadece 0 ve 1 içermelidir.")
            return
        if len(data) not in [8, 16, 32]:
            messagebox.showerror("Hata", "Veri uzunluğu 8, 16 veya 32 bit olmalıdır.")
            return

        hamming = calculate_hamming_code(data)
        status = "Normal"
        self.memory.append((data, hamming, status))

        index = len(self.memory)
        self.tree.insert("", tk.END, values=(index, data, hamming, status))
        self.data_entry.delete(0, tk.END)

    def introduce_error(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir satır seçin.")
            return

        item_id = selected[0]
        index = int(self.tree.item(item_id, "values")[0]) - 1
        data, hamming, _ = self.memory[index]

        flip_index = random.randint(0, len(hamming) - 1)
        errored = bit_flip(hamming, flip_index)

        self.memory[index] = (data, errored, f"Hatalı (bit {flip_index})")
        self.tree.item(item_id, values=(index + 1, data, errored, f"Hatalı (bit {flip_index})"))

    def correct_error(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir satır seçin.")
            return

        item_id = selected[0]
        index = int(self.tree.item(item_id, "values")[0]) - 1
        data, hamming, _ = self.memory[index]

        message, corrected = detect_and_correct(hamming)
        self.memory[index] = (data, corrected, "Düzeltilmiş")

        self.tree.item(item_id, values=(index + 1, data, corrected, "Düzeltilmiş"))
        messagebox.showinfo("Düzeltme Sonucu", message)

# --- Programı Başlat ---
if __name__ == "__main__":
    root = tk.Tk()
    app = HammingSimulator(root)
    root.mainloop()
