import tkinter as tk
import random
import time
import matplotlib.pyplot as plt
import numpy as np

# Constants
MAX_LINES = 3
MAX_BET = 500
MIN_BET = 1
ROWS = 3
COLS = 3
JACKPOT_MULTIPLIER = 3
AUTO_SPIN_DELAY = 1000  # Milliseconds
WIN_PROBABILITY = 0.5  # 50% win ratio
WIN_MULTIPLIER = 2.0  # Changed to 2x for wins
LOSS_MULTIPLIER = 2  # 2x for losses
BONUS_ROUND_THRESHOLD = 3  # Number of consecutive wins to trigger bonus round

# Symbols and Values
symbol_count = {
    "🍒": 2,
    "🍋": 4,
    "🍊": 6,
    "🍉": 8
}

symbol_value = {
    "🍒": 5,
    "🍋": 4,
    "🍊": 6,
    "🍉": 3
}

def check_winning(columns, lines, bet):
    winnings = 0
    winning_lines = []
    jackpot = True
    
    # Check each line for wins
    for line in range(lines):
        # For horizontal lines, we need to check the symbols in each column at the same row position
        first_symbol = columns[0][line]
        is_winner = True
        
        # Check if all symbols in this line match the first symbol
        for col in range(COLS):
            if columns[col][line] != first_symbol:
                is_winner = False
                jackpot = False
                break
                
        if is_winner:
            winnings += symbol_value[first_symbol] * bet * WIN_MULTIPLIER
            winning_lines.append(line + 1)

    if jackpot:
        winnings *= JACKPOT_MULTIPLIER
    
    return winnings, winning_lines, jackpot

def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = [symbol for symbol, count in symbols.items() for _ in range(count)]
    if random.random() < WIN_PROBABILITY:
        winning_symbol = random.choice(list(symbol_value.keys()))
        return [[winning_symbol] * rows for _ in range(cols)]
    else:
        return [[random.choice(all_symbols) for _ in range(rows)] for _ in range(cols)]

class SlotMachineGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Casino Slot Machine")
        self.root.geometry("800x750")
        self.root.configure(bg="#2E2E2E")
        self.balance = 1000
        self.total_winnings = 0
        self.total_losses = 0
        self.balance_history = [self.balance]  # Track balance history
        self.rounds = [0]  # Track the number of spins
        self.auto_spin = False
        self.consecutive_wins = 0  # Track consecutive wins
        self.create_widgets()
        self.update_balance_display()
    
    def create_widgets(self):
        title_label = tk.Label(self.root, text="🎰 Casino Slot Machine 🎰", font=("Arial", 24, "bold"), bg="#2E2E2E", fg="#FFD700")
        title_label.pack(pady=20)

        self.balance_label = tk.Label(self.root, text=f"Balance: ${self.balance}", font=("Arial", 18), bg="#2E2E2E", fg="#FFFFFF")
        self.balance_label.pack(pady=10)

        self.bet_label = tk.Label(self.root, text="Bet per Line ($1 - $500):", font=("Arial", 14), bg="#2E2E2E", fg="#FFFFFF")
        self.bet_label.pack()
        self.bet_entry = tk.Entry(self.root, font=("Arial", 14))
        self.bet_entry.pack(pady=5)

        self.lines_label = tk.Label(self.root, text="Lines (1-3):", font=("Arial", 14), bg="#2E2E2E", fg="#FFFFFF")
        self.lines_label.pack()
        self.lines_entry = tk.Entry(self.root, font=("Arial", 14))
        self.lines_entry.pack(pady=5)

        self.spin_button = tk.Button(self.root, text="Spin", command=self.spin_slot, font=("Arial", 18, "bold"), bg="#4CAF50", fg="white")
        self.spin_button.pack(pady=20)

        self.win_loss_label = tk.Label(self.root, text="", font=("Arial", 16), bg="#2E2E2E", fg="#FFFFFF")
        self.win_loss_label.pack(pady=5)

        self.auto_spin_button = tk.Button(self.root, text="Auto Spin", command=self.auto_spin_toggle, font=("Arial", 14, "bold"), bg="#FFA500", fg="white")
        self.auto_spin_button.pack(pady=5)

        self.result_label = tk.Label(self.root, text="", font=("Arial", 18), bg="#2E2E2E", fg="#FFD700")
        self.result_label.pack(pady=10)

        self.slot_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.slot_frame.pack(pady=10)

        self.column_labels = [tk.Label(self.slot_frame, text="", font=("Arial", 30), bg="#2E2E2E", fg="#FFFFFF") for _ in range(COLS)]
        for label in self.column_labels:
            label.pack(side=tk.LEFT, padx=10)

        self.chart_button = tk.Button(self.root, text="Show Stats", command=self.show_stats, font=("Arial", 14), bg="#008CBA", fg="white")
        self.chart_button.pack(pady=10)

    def update_balance_display(self):
        self.balance_label.config(text=f"Balance: ${self.balance}")

    def animate_spin(self):
        for _ in range(10):
            for label in self.column_labels:
                label.config(text=random.choice(list(symbol_value.keys())))
            self.root.update()
            time.sleep(0.1)

    def spin_slot(self):
        bet = self.validate_input()
        if bet is None:
            return

        self.animate_spin()
        final_columns = get_slot_machine_spin(ROWS, COLS, symbol_count)
        for col_idx, column in enumerate(final_columns):
            self.column_labels[col_idx].config(text=" | ".join(column))
        
        lines = int(self.lines_entry.get())
        total_bet = bet * lines
        winnings, winning_lines, _ = check_winning(final_columns, lines, bet)
        
        # Apply LOSS_MULTIPLIER to losses
        if winnings == 0:
            total_bet *= LOSS_MULTIPLIER
            self.consecutive_wins = 0  # Reset consecutive wins on loss
        else:
            self.consecutive_wins += 1  # Increment consecutive wins

        self.balance -= total_bet
        self.balance += winnings

        self.balance_history.append(self.balance)
        self.rounds.append(len(self.rounds))

        if winnings > 0:
            self.total_winnings += winnings
            self.win_loss_label.config(text=f"You won: ${winnings}", fg="green")
            if self.consecutive_wins >= BONUS_ROUND_THRESHOLD:
                self.bonus_game()  # Trigger bonus game
        else:
            self.total_losses += total_bet
            self.win_loss_label.config(text=f"You lost: ${total_bet}", fg="red")

        self.update_balance_display()

        if self.auto_spin:
            self.root.after(AUTO_SPIN_DELAY, self.spin_slot)

    def validate_input(self):
        try:
            bet = int(self.bet_entry.get())
            lines = int(self.lines_entry.get())
            if self.balance <= 0:
                raise ValueError("Game over! No balance remaining.")
            if bet < MIN_BET or bet > MAX_BET:
                raise ValueError("Bet must be between $1 and $500.")
            if lines < 1 or lines > MAX_LINES:
                raise ValueError("Lines must be between 1 and 3.")
            if bet * lines > self.balance:
                raise ValueError("Not enough balance for this bet.")
            return bet
        except ValueError as e:
            self.win_loss_label.config(text=f"Error: {str(e)}", fg="red")
            return None

    def auto_spin_toggle(self):
        self.auto_spin = not self.auto_spin
        if self.auto_spin:
            self.spin_slot()

    def show_stats(self):
        # Calculate percentage changes for coloring
        pct_changes = [(self.balance_history[i] - self.balance_history[i-1])/self.balance_history[i-1]*100 
                       for i in range(1, len(self.balance_history))]
        pct_changes.insert(0, 0)

        # Create figure with professional trading chart theme
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1], gridspec_kw={'hspace': 0.3})
        fig.patch.set_facecolor('#1c1c1c')
        ax1.set_facecolor('#1c1c1c')
        ax2.set_facecolor('#1c1c1c')

        # Main price chart
        ax1.plot(self.rounds, self.balance_history, 
                color='#00ff00', linewidth=1.5, alpha=0.8)

        # Calculate moving averages
        window_20 = 5 if len(self.balance_history) > 5 else len(self.balance_history)
        window_50 = 10 if len(self.balance_history) > 10 else len(self.balance_history)
        
        if len(self.balance_history) > window_20:
            ma20 = np.convolve(self.balance_history, np.ones(window_20)/window_20, mode='valid')
            ax1.plot(self.rounds[window_20-1:], ma20, '--', color='#ff9900', label=f'MA{window_20}', alpha=0.7)
        
        if len(self.balance_history) > window_50:
            ma50 = np.convolve(self.balance_history, np.ones(window_50)/window_50, mode='valid')
            ax1.plot(self.rounds[window_50-1:], ma50, '--', color='#00ffff', label=f'MA{window_50}', alpha=0.7)

        # Volume-like bars in bottom chart
        colors = ['#00ff00' if p >= 0 else '#ff0000' for p in pct_changes]
        ax2.bar(self.rounds, np.abs(pct_changes), color=colors, alpha=0.7)
        ax2.set_ylabel('Change %', color='white', fontsize=10)

        # Customize grids
        ax1.grid(True, linestyle='--', alpha=0.2)
        ax2.grid(True, linestyle='--', alpha=0.2)

        # Customize labels and title
        ax1.set_title('SLOT-50 Trading Chart', color='white', fontsize=14, pad=20)
        ax1.set_ylabel('Balance ($)', color='white', fontsize=12)
        
        # Add stats box
        win_rate = sum(1 for x in pct_changes[1:] if x > 0) / (len(pct_changes)-1) * 100
        stats_text = (f'Win Rate: {win_rate:.1f}%\n'
                    f'Initial: ${self.balance_history[0]:,.2f}\n'
                    f'Current: ${self.balance_history[-1]:,.2f}\n'
                    f'Change: {((self.balance_history[-1]/self.balance_history[0])-1)*100:.1f}%')
        
        # Add stats box with semi-transparent background
        bbox_props = dict(boxstyle='round,pad=0.5', facecolor='#1c1c1c', alpha=0.7, edgecolor='white')
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                 verticalalignment='top', color='white', bbox=bbox_props, fontsize=10)

        # Customize ticks
        for ax in [ax1, ax2]:
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white') 
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')

        # Add legend
        ax1.legend(loc='upper right', facecolor='#1c1c1c', edgecolor='white', labelcolor='white')

        plt.tight_layout()
        plt.show()

    def bonus_game(self):
        bonus_winnings = random.randint(100, 500)  # Random bonus winnings
        self.balance += bonus_winnings
        self.win_loss_label.config(text=f"Bonus Game! You won an extra: ${bonus_winnings}", fg="gold")
        self.consecutive_wins = 0  # Reset consecutive wins after bonus round

        # Bonus game UI
        bonus_window = tk.Toplevel(self.root)
        bonus_window.title("Bonus Game")
        bonus_window.geometry("400x300")
        bonus_label = tk.Label(bonus_window, text="Welcome to the Bonus Game!", font=("Arial", 18))
        bonus_label.pack(pady=20)

        bonus_result_label = tk.Label(bonus_window, text=f"You can win up to ${bonus_winnings}!", font=("Arial", 14))
        bonus_result_label.pack(pady=10)

        spin_button = tk.Button(bonus_window, text="Spin for Bonus!", command=lambda: self.spin_for_bonus(bonus_window, bonus_result_label), font=("Arial", 14), bg="#4CAF50", fg="white")
        spin_button.pack(pady=20)

        close_button = tk.Button(bonus_window, text="Close", command=bonus_window.destroy, font=("Arial", 14), bg="#FF5733", fg="white")
        close_button.pack(pady=10)

    def spin_for_bonus(self, bonus_window, bonus_result_label):
        # Simulate a spin for bonus
        spin_result = random.choice(["Win", "Lose"])
        if spin_result == "Win":
            bonus_amount = random.randint(50, 200)  # Random bonus amount
            self.balance += bonus_amount
            bonus_result_label.config(text=f"You won an extra: ${bonus_amount}!", fg="green")
        else:
            bonus_result_label.config(text="You lost the bonus spin!", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    game = SlotMachineGame(root)
    root.mainloop()
