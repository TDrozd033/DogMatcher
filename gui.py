import tkinter as tk 
import main as api  
from PIL import Image, ImageTk  
from tkinter import PhotoImage  
import requests 
from io import BytesIO  

class DogMatcherApp:
    # inicjujemy aplikacje
    def __init__(self, root):
        self.root = root  
        self.root.title("Dog Matcher")  #tytuł okna aplikacji
        self.root.geometry("800x700")  # rozmiar okna aplikacji
        self.root.configure(bg="#FFDAB9") 
        self.root.iconphoto(False, PhotoImage(file='dog.png')) 

        self.start_screen()  

    # okno startowe
    def start_screen(self):
        self.clear_screen()  # czyści wszystkie widgety z poprzednich ekranów
        # label powitalny
        title_label = tk.Label(
            self.root,
            text="Welcome to Dog Matcher!",  
            font=("Arial", 28, "bold"),  
            bg="#9400D3",  
            fg="white",  
            pady=10  
        )
        title_label.pack(fill="x")  # tytul na cala szerokosc okna
        subtitle_label = tk.Label(
            self.root,
            text="Find your perfect furry friend!",  
            font=("Arial", 16),  
            bg="#5f9ea0",  
            fg="white",  
            pady=5,  
        )
        subtitle_label.pack(fill="x") 
        
        # zdjęcie na oknie startowym
        image_path = "dog.jpeg"  
        original_image = Image.open(image_path)  
        resized_image = original_image.resize((300, 300)) 
        self.image = ImageTk.PhotoImage(resized_image) 

        image_label = tk.Label(self.root, image=self.image, bg="#f0f8ff") 
        image_label.pack(pady=20)  
        # przycisk start który przenosi do następnego okna
        start_button = tk.Button(
            self.root,
            text="Start", 
            font=("Helvetica", 14),  
            bg="#32cd32",  
            fg="white",  
            command=self.main_screen,  # przejście do głównego ekranu
            relief="solid",  
            bd=3,  
            padx=20,  
            pady=10 
        )
        start_button.config(
            highlightthickness=0,  
            activebackground="#32cd32",  
            activeforeground="white",  
            borderwidth=0  
        )
        start_button.pack(pady=10)  

    # widok główny, odpowiadanie na pytania 
    def main_screen(self):
        self.clear_screen()  

        title_label = tk.Label(
            self.root,
            text="Welcome to Dog Matcher!",  
            font=("Arial", 28, "bold"), 
            bg="#9400D3",  
            fg="white",  
            pady=10  
        )
        title_label.pack(fill="x")  
        subtitle_label = tk.Label(
            self.root,
            text="Find your perfect furry friend!",  
            font=("Arial", 16), 
            bg="#5f9ea0",  
            fg="white",  
            pady=5,  
        )
        subtitle_label.pack(fill="x")  
        # ramka pytanie
        qa_frame = tk.Frame(self.root, bg="white", bd=3, relief="solid")  # ramka na pytanie
        qa_frame.place(relx=0.5, rely=0.25, relwidth=0.9, relheight=0.2, anchor="n")  # ustawia ramkę w odpowiednim miejscu

        self.question_label = tk.Label(
            qa_frame,
            #text="Click 'Start' to begin!",
            font=("Helvetica", 14),  
            bg="white", 
            anchor="w"  
        )
        self.question_label.place(relwidth=1, relheight=0.4)  # ustawia etykietę pytania w odpowiednim miejscu
        # miejsce na odp
        self.answer_entry = tk.Entry(qa_frame, font=("Arial", 14), bd=3, relief="solid")  # pole tekstowe na odpowiedź
        self.answer_entry.place(rely=0.5, relwidth=0.7, relheight=0.4)  # ustawia pole tekstowe na odpowiedź

        self.answer_entry.bind("<Return>", self.next_question)  # klikniecie w  klawisz Enter -> przejście do kolejnego pytania
        
        # przycisk do zatwierdzania i przeejscia do kolejnego pytania 
        submit_button = tk.Button(
            qa_frame,
            text="Submit",  
            font=("Helvetica", 12),  
            bg="#4B0082",  
            fg="white",  
            command=self.next_question,  
            relief="solid",
            bd=3, 
            padx=20, 
            pady=10  
        )
        submit_button.config(
            highlightthickness=0,  
            activebackground="#4682b4",  
            activeforeground="white", 
            borderwidth=0  
        )
        submit_button.place(relx=0.72, rely=0.5, relwidth=0.25, relheight=0.4)  

        self.answers = []  # lista odpowiedzi
        self.questions = [q[0] for q in api.filters]  # lista pytań
        self.current_question = 0  

        self.start_quiz()  

    def start_quiz(self):
        self.question_label.config(text=self.questions[0])  # ustawia pierwsze pytanie

    def next_question(self, event=None):
        """ Ta metoda będzie wywołana jeśli klikniemy klawisz Enter lub naciśniemy przycisk Submit """
        answer = self.answer_entry.get().strip()  # pobiera odp
        self.answers.append(answer)  # zapisuje odp
        self.answer_entry.delete(0, tk.END)  # czyści pole 
        

        if self.current_question < len(self.questions) - 1:  # sprawdza, czy są jeszcze pytania
            self.current_question += 1  
            self.question_label.config(text=self.questions[self.current_question])  # ustawia nowe pytanie
        else:
            self.final_screen()  # przechodzi do ekranu końcowego

    def final_screen(self):
        self.clear_screen() 
        
        title_label = tk.Label(
            self.root,
            text="Your Perfect Match!",  
            font=("Arial", 28, "bold"), 
            bg="#32CD32",  
            fg="white",  
            pady=10  #
        )
        title_label.pack(fill="x") 

        result = api.process_user_input(self.answers)  # przetwarzanie odpowiedzi w celu dopasowania psa
        
        if result and isinstance(result, tuple) and len(result) >= 3:  
            breed, description, image_url = result[:3]  # przypisanie wartości dla rasy, opisu i URL do obrazu
        else:
            breed, description, image_url = "Brak wyników", "Nie znaleziono dopasowanej rasy psa.", None  

        data_frame = tk.Frame(self.root, bg="white", bd=3, relief="solid")  
        data_frame.place(relx=0.5, rely=0.2, relwidth=0.9, relheight=0.3, anchor="n")  

        self.data_display = tk.Text(
            data_frame,
            font=("Georgia", 13), 
            bg="#f5f5f5", 
            state="normal",  
            wrap="word",  
            padx=10,  
            pady=10  
        )

        self.data_display.tag_configure("center", justify="center")  
        self.data_display.tag_configure("bold_center", font=("Georgia", 13, "bold"), justify="center")  

        self.data_display.insert(tk.END, f"Najlepiej dobrana rasa: {breed}\n", "bold_center")  
        self.data_display.insert(tk.END, f"{description}\n") 

        self.data_display.config(state="disabled")  
        self.data_display.pack(fill="both", expand=True)  

        if image_url:  
            response = requests.get(image_url) 
            img_data = Image.open(BytesIO(response.content))  # otwieranie obrazu
            img_data = img_data.resize((300, 300)) 
            self.dog_image = ImageTk.PhotoImage(img_data)  
            image_label = tk.Label(self.root, image=self.dog_image, bg="#f7f7f7")  
            image_label.place(relx=0.5, rely=0.55, anchor="n")  
        
        home_button = tk.Button(
            self.root,
            text="Home",  
            font=("Helvetica", 14),  
            bg="#8B0000", 
            fg="white",  
            command=self.start_screen,  
            relief="solid",  
            bd=3,  
            padx=20, 
            pady=10  #
        )
        home_button.config(
            highlightthickness=0, 
            activebackground="#ff6347",  
            activeforeground="white",  
            borderwidth=0  
        )
        home_button.pack(pady=0)  

    def clear_screen(self):
        for widget in self.root.winfo_children(): 
            widget.destroy()  

if __name__ == "__main__": 
    root = tk.Tk()  # główne okno aplikacji
    app = DogMatcherApp(root)  
    root.mainloop() 
        