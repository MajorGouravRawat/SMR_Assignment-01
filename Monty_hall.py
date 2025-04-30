import streamlit as st
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

class MontyHallGame:
    def __init__(self):
        self.doors = ['goat', 'goat', 'car']
        self.first_choice = None
        self.opened_door = None
        self.final_choice = None
        self.wins_stay = 0
        self.wins_switch = 0
        self.total_games = 0
        self.game_history = []
        
        # Visual style
        self.colors = {
            'door': '#3498db',
            'selected': '#e74c3c',
            'opened': '#95a5a6',
            'car': '#2ecc71',
            'goat': '#e67e22',
            'text': '#2c3e50'
        }
    
    def shuffle_doors(self):
        random.shuffle(self.doors)
        self.first_choice = None
        self.opened_door = None
        self.final_choice = None
    
    def play_game(self, strategy):
        """Play one game with the given strategy ('stay' or 'switch')"""
        self.shuffle_doors()
        first_choice = random.randint(0, 2)
        
        # Host opens a door
        for i in range(3):
            if i != first_choice and self.doors[i] != 'car':
                opened_door = i
                break
        
        # Apply strategy
        if strategy == 'switch':
            for i in range(3):
                if i != first_choice and i != opened_door:
                    final_choice = i
        else:
            final_choice = first_choice
        
        # Record result
        won = self.doors[final_choice] == 'car'
        if strategy == 'stay':
            self.wins_stay += won
        else:
            self.wins_switch += won
        
        self.total_games += 1
        self.game_history.append({
            'game': self.total_games,
            'strategy': strategy,
            'won': won,
            'first_choice': first_choice,
            'opened_door': opened_door,
            'final_choice': final_choice,
            'car_position': self.doors.index('car')
        })
        
        return {
            'won': won,
            'first_choice': first_choice,
            'opened_door': opened_door,
            'final_choice': final_choice,
            'car_position': self.doors.index('car'),
            'strategy': strategy
        }

def visualize_single_game(result):
    """Create a visual representation of a single game"""
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.title("Monty Hall Game Result", color='#2c3e50', pad=20)
    
    # Draw doors
    doors = []
    colors = []
    for i in range(3):
        color = '#3498db'  # Default door color
        if i == result['opened_door']:
            color = '#95a5a6'  # Opened door
        elif i == result['first_choice']:
            color = '#e74c3c'  # Initially selected
        elif i == result['final_choice']:
            color = '#f39c12'  # Final choice
        
        doors.append(Rectangle((i, 0), 0.8, 2))
        colors.append(color)
        
        # Show what's behind the opened door
        if i == result['opened_door']:
            plt.text(i + 0.4, 1, 'GOAT' if result['opened_door'] != result['car_position'] else 'CAR', 
                    ha='center', va='center', fontsize=12, color='white', weight='bold')
        
        plt.text(i + 0.4, 2.2, f"Door {i+1}", 
                ha='center', va='center', fontsize=12, color='#2c3e50')
    
    # Add collection of doors
    pc = PatchCollection(doors, facecolor=colors, edgecolor='black')
    ax.add_collection(pc)
    
    # Add annotations
    strategy_text = "stayed" if result['strategy'] == 'stay' else "switched"
    outcome_text = "WON 🎉" if result['won'] else "lost 😢"
    
    plt.text(1.5, 3, f"Initial choice: Door {result['first_choice'] + 1}", 
            fontsize=12, color='#e74c3c', ha='center')
    plt.text(1.5, 2.7, f"Host opens: Door {result['opened_door'] + 1}", 
            fontsize=12, color='#95a5a6', ha='center')
    plt.text(1.5, 2.4, f"You {strategy_text} to Door {result['final_choice'] + 1} and {outcome_text}", 
            fontsize=12, color='#2c3e50', ha='center')
    
    # Hide axes
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.axis('off')
    
    plt.tight_layout()
    st.pyplot(fig)

def plot_statistics(game_history, wins_stay, wins_switch, total_games):
    """Plot the statistics of all games played"""
    if total_games == 0:
        return
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart of wins by strategy
    strategies = ['Stay', 'Switch']
    win_counts = [wins_stay, wins_switch]
    bars = ax1.bar(strategies, win_counts, color=['#e74c3c', '#3498db'])
    ax1.set_title('Wins by Strategy')
    ax1.set_ylabel('Number of Wins')
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}\n({height/total_games*100:.1f}%)',
                ha='center', va='bottom')
    
    # Line chart of cumulative win percentage
    if len(game_history) > 0:
        df = pd.DataFrame(game_history)
        df['cum_stay'] = df[df['strategy'] == 'stay']['won'].cumsum()
        df['cum_switch'] = df[df['strategy'] == 'switch']['won'].cumsum()
        df['games_stay'] = (df['strategy'] == 'stay').cumsum()
        df['games_switch'] = (df['strategy'] == 'switch').cumsum()
        
        # Calculate cumulative win percentages
        df['stay_pct'] = df['cum_stay'] / df['games_stay'] * 100
        df['switch_pct'] = df['cum_switch'] / df['games_switch'] * 100
        
        ax2.plot(df['game'], df['stay_pct'], label='Stay', color='#e74c3c')
        ax2.plot(df['game'], df['switch_pct'], label='Switch', color='#3498db')
        ax2.set_title('Win Percentage Over Time')
        ax2.set_xlabel('Game Number')
        ax2.set_ylabel('Win Percentage')
        ax2.legend()
        ax2.set_ylim(0, 100)
        ax2.axhline(y=100/3, color='#95a5a6', linestyle='--', alpha=0.5)
        ax2.axhline(y=200/3, color='#95a5a6', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    st.pyplot(fig)

def main():
    st.set_page_config(page_title="Monty Hall Simulator", layout="wide")
    
    # Initialize session state
    if 'game' not in st.session_state:
        st.session_state.game = MontyHallGame()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .sub-title {
        font-size: 1.2em;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2em;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    .stSelectbox>div>div>select {
        border-radius: 5px;
    }
    .result-box {
        border-radius: 5px;
        padding: 1em;
        margin: 1em 0;
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-title">Monty Hall Problem Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Explore the counterintuitive probabilities behind this classic puzzle</div>', unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Game Controls")
        mode = st.radio("Select Mode:", ("Interactive Game", "Automatic Simulation", "Educational Demo"))
        
        if mode == "Interactive Game":
            st.markdown("### Play a Single Game")
            door_choice = st.selectbox("Choose a door:", [1, 2, 3], index=0)
            strategy = st.radio("After a goat is revealed:", ["Stay with initial choice", "Switch to other door"])
            
            if st.button("Play Game"):
                # Play the game
                st.session_state.game.shuffle_doors()
                first_choice = door_choice - 1
                
                # Host opens a door
                for i in range(3):
                    if i != first_choice and st.session_state.game.doors[i] != 'car':
                        opened_door = i
                        break
                
                # Apply strategy
                if strategy == "Switch to other door":
                    for i in range(3):
                        if i != first_choice and i != opened_door:
                            final_choice = i
                else:
                    final_choice = first_choice
                
                # Determine result
                won = st.session_state.game.doors[final_choice] == 'car'
                
                # Record statistics
                if strategy == "Stay with initial choice":
                    st.session_state.game.wins_stay += won
                else:
                    st.session_state.game.wins_switch += won
                
                st.session_state.game.total_games += 1
                st.session_state.game.game_history.append({
                    'game': st.session_state.game.total_games,
                    'strategy': 'stay' if strategy == "Stay with initial choice" else 'switch',
                    'won': won,
                    'first_choice': first_choice,
                    'opened_door': opened_door,
                    'final_choice': final_choice,
                    'car_position': st.session_state.game.doors.index('car')
                })
                
                # Show result
                result = {
                    'won': won,
                    'first_choice': first_choice,
                    'opened_door': opened_door,
                    'final_choice': final_choice,
                    'car_position': st.session_state.game.doors.index('car'),
                    'strategy': 'stay' if strategy == "Stay with initial choice" else 'switch'
                }
                
                st.session_state.last_result = result
        
        elif mode == "Automatic Simulation":
            st.markdown("### Run Simulations")
            strategy = st.radio("Simulation Strategy:", ["Stay", "Switch"])
            num_games = st.slider("Number of games:", 10, 10000, 1000, 10)
            
            if st.button(f"Run {num_games} Games"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                wins = 0
                for i in range(num_games):
                    result = st.session_state.game.play_game(strategy.lower())
                    if result['won']:
                        wins += 1
                    
                    if i % 100 == 0 or i == num_games - 1:
                        progress_bar.progress((i + 1) / num_games)
                        status_text.text(f"Running... {i+1}/{num_games} games completed")
                
                win_percentage = (wins / num_games) * 100
                st.success(f"Won {wins}/{num_games} games ({win_percentage:.1f}%) by choosing to {strategy.lower()}")
        
        elif mode == "Educational Demo":
            if st.button("Run Educational Demo"):
                st.session_state.run_demo = True
    
    # Main content area
    if mode == "Interactive Game" and 'last_result' in st.session_state:
        st.markdown("## Game Result")
        visualize_single_game(st.session_state.last_result)
        
        if st.session_state.last_result['won']:
            st.success("🎉 Congratulations! You won the car! 🚗")
        else:
            st.error("🐐 Sorry, it's a goat! Better luck next time!")
        
        st.markdown("### What happened?")
        if st.session_state.last_result['strategy'] == 'stay':
            st.write(f"You initially chose Door {st.session_state.last_result['first_choice'] + 1} and stayed with it.")
        else:
            st.write(f"You initially chose Door {st.session_state.last_result['first_choice'] + 1} and switched to Door {st.session_state.last_result['final_choice'] + 1}.")
        
        st.write(f"The car was actually behind Door {st.session_state.last_result['car_position'] + 1}.")
    
    elif mode == "Educational Demo" and 'run_demo' in st.session_state:
        st.markdown("""
        ## 🎲 Monty Hall Problem Demo
        
        You're a contestant on a game show. You're shown 3 doors:
        - Behind one door is a car (🚗)
        - Behind the other two are goats (🐐)
        
        You pick a door (say, Door 1). The host, who knows what's behind
        the doors, opens another door (say, Door 3) which has a goat.
        
        You're then given a choice: 
        - **STAY** with your original choice (Door 1), or
        - **SWITCH** to the remaining unopened door (Door 2)
        
        What should you do to maximize your chances of winning the car?
        """)
        
        if st.button("Show me the probabilities!"):
            # Run simulations
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run stay strategy
            status_text.text("Running simulations for 'Stay' strategy...")
            wins_stay = 0
            for i in range(1000):
                result = st.session_state.game.play_game('stay')
                if result['won']:
                    wins_stay += 1
                if i % 100 == 0:
                    progress_bar.progress(i / 2000)
            
            # Run switch strategy
            status_text.text("Running simulations for 'Switch' strategy...")
            wins_switch = 0
            for i in range(1000, 2000):
                result = st.session_state.game.play_game('switch')
                if result['won']:
                    wins_switch += 1
                if i % 100 == 0:
                    progress_bar.progress(i / 2000)
            
            progress_bar.empty()
            status_text.empty()
            
            st.markdown(f"""
            ### 💡 The Counterintuitive Result
            
            After running 1000 games for each strategy:
            
            - **Staying** with your initial choice: **{wins_stay/10:.1f}%** win rate
            - **Switching** doors: **{wins_switch/10:.1f}%** win rate
            
            This seems paradoxical at first, but makes sense when you consider:
            1. Your first choice has a 1/3 chance of being correct
            2. So there's a 2/3 chance the car is behind one of the other doors
            3. The host's action of revealing a goat gives you additional information
            4. By switching, you capitalize on the initial 2/3 probability
            
            This classic probability puzzle demonstrates how our intuition can sometimes
            lead us astray when dealing with conditional probabilities!
            """)
    
    # Show statistics if we have any games played
    if st.session_state.game.total_games > 0:
        st.markdown("## Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Games Played", st.session_state.game.total_games)
        with col2:
            st.metric("Current Win Rate", 
                     f"{(st.session_state.game.wins_stay + st.session_state.game.wins_switch) / st.session_state.game.total_games * 100:.1f}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Wins by Staying", 
                     f"{st.session_state.game.wins_stay} ({st.session_state.game.wins_stay/st.session_state.game.total_games*100:.1f}%)")
        with col2:
            st.metric("Wins by Switching", 
                     f"{st.session_state.game.wins_switch} ({st.session_state.game.wins_switch/st.session_state.game.total_games*100:.1f}%)")
        
        plot_statistics(st.session_state.game.game_history, 
                       st.session_state.game.wins_stay, 
                       st.session_state.game.wins_switch, 
                       st.session_state.game.total_games)
        
        # Show raw data if requested
        if st.checkbox("Show raw game data"):
            st.dataframe(pd.DataFrame(st.session_state.game.game_history))

if __name__ == "__main__":
    main()