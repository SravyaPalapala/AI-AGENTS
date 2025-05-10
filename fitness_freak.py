import os
import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

GOOGLE_API_KEY = "AIzaSyCr35hxFrpVsbNWgqOwU6PwmkpwLmO2dJA"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Dietary Planner Agent
dietary_planner = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Creates personalized dietary plans based on user input.",
    instructions=[
        "Generate a diet plan with breakfast, lunch, dinner, and snacks.",
        "Consider dietary preferences like Keto, Vegetarian, or Low Carb.",
        "Ensure proper hydration and electrolyte balance.",
        "Provide nutritional breakdown including macronutrients and vitamins.",
        "Suggest meal preparation tips for easy implementation.",
        "If necessary, search the web using DuckDuckGo for additional information.",
    ],
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True
)

# Function to get a personalized meal plan
def get_meal_plan(age, weight, height, activity_level, dietary_preference, fitness_goal):
    prompt = (f"Create a personalized meal plan for a {age}-year-old person, weighing {weight}kg, "
              f"{height}cm tall, with an activity level of '{activity_level}', following a "
              f"'{dietary_preference}' diet, aiming to achieve '{fitness_goal}'.")
    return dietary_planner.run(prompt)

# Fitness Trainer Agent
fitness_trainer = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Generates customized workout routines based on fitness goals.",
    instructions=[
        "Create a workout plan including warm-ups, main exercises, and cool-downs.",
        "Adjust workouts based on fitness level: Beginner, Intermediate, Advanced.",
        "Consider weight loss, muscle gain, endurance, or flexibility goals.",
        "Provide safety tips and injury prevention advice.",
        "Suggest progress tracking methods for motivation.",
        "If necessary, search the web using DuckDuckGo for additional information.",
    ],
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True
)

# Function to get a personalized fitness plan
def get_fitness_plan(age, weight, height, activity_level, fitness_goal):
    prompt = (f"Generate a workout plan for a {age}-year-old person, weighing {weight}kg, "
              f"{height}cm tall, with an activity level of '{activity_level}', "
              f"aiming to achieve '{fitness_goal}'. Include warm-ups, exercises, and cool-downs.")
    return fitness_trainer.run(prompt)

# Team Lead Agent (combines both meal and fitness plans)
team_lead = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Combines diet and workout plans into a holistic health strategy.",
    instructions=[
        "Merge personalized diet and fitness plans for a comprehensive approach, Use Tables if possible.",
        "Ensure alignment between diet and exercise for optimal results.",
        "Suggest lifestyle tips for motivation and consistency.",
        "Provide guidance on tracking progress and adjusting plans over time."
    ],
    markdown=True
)

# Function to get a full health plan
def get_full_health_plan(name, age, weight, height, activity_level, dietary_preference, fitness_goal):
    meal_plan = get_meal_plan(age, weight, height, activity_level, dietary_preference, fitness_goal)
    fitness_plan = get_fitness_plan(age, weight, height, activity_level, fitness_goal)

    return team_lead.run(
        f"Greet the customer,{name}\n\n"
        f"User Information: {age} years old, {weight}kg, {height}cm, activity level: {activity_level}.\n\n"
        f"Fitness Goal: {fitness_goal}\n\n"
        f"Meal Plan:\n{meal_plan}\n\n"
        f"Workout Plan:\n{fitness_plan}\n\n"
        f"Provide a holistic health strategy integrating both plans."
    )


# Set up Streamlit UI with a fitness theme
st.set_page_config(page_title="AI Health & Fitness Plan", page_icon="🏋️‍♂️", layout="wide")

# Custom Styles for a Fitness and Health Theme
# Custom Styles with 3D Effects
st.markdown("""
    <style>
        /* 3D GENERATE BUTTON */
        .stButton>button {
            background: linear-gradient(to bottom, #FF6347, #E5533D) !important;
            color: white !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 0 #C44532, 0 6px 8px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.1s ease !important;
        }
        .stButton>button:active {
            transform: translateY(4px) !important;
            box-shadow: 0 1px 0 #C44532 !important;
        }

        /* 3D INPUT CARD (My Health Mission) */
        div[data-testid="stVerticalBlock"]:has(> div > div > .stMarkdown > h3) {
            background: white !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.1),
                        0 4px 8px -2px rgba(0, 0, 0, 0.06) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        div[data-testid="stVerticalBlock"]:has(> div > div > .stMarkdown > h3):hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.12),
                        0 8px 16px -4px rgba(0, 0, 0, 0.08) !important;
        }

        /* 3D TITLE */
        .title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #1E90FF;
            border: 3px solid #1E90FF;
            border-radius: 10px;
            padding: 10px;
            display: inline-block;
            margin: 0 auto;
            background-color: #F0F8FF;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            box-shadow: 0 8px 16px rgba(30, 144, 255, 0.2);
        }

        /* MAROON SIDEBAR (KEPT FROM ORIGINAL) */
        [data-testid="stSidebar"] {
            background-color: #FFF0F0 !important;
            padding: 20px !important;
            border-radius: 10px !important;
            border-left: 5px solid #800000 !important;
        }
        [data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
            color: #800000 !important;
        }
        [data-testid="stSidebar"] .st-emotion-cache-1h9usn1 {
            color: #A52A2A !important;
        }

        /* REST OF YOUR ORIGINAL CSS (UNCHANGED) */
        .subtitle {
            text-align: center;
            font-size: 24px;
            color: #4CAF50;
        }
        .content {
            padding: 20px;
            background-color: #E0F7FA;
            border-radius: 10px;
            margin-top: 20px;
        }
        .goal-card {
            padding: 20px;
            margin: 10px;
            background-color: #FFF;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Title and Subtitle
st.markdown('<h1 class="title">🏋️‍♂️ FitGenie:"Your AI Fitness Coach"</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Personalized fitness and nutrition plans to help you achieve your health goals!!</p>', unsafe_allow_html=True)

st.sidebar.header("Personal Information")
st.sidebar.subheader("Customize Your Plan")

# User inputs for personal information and fitness goals
age = st.sidebar.number_input("Age (in years)", min_value=10, max_value=100, value=25)
weight = st.sidebar.number_input("Weight (in kg)", min_value=30, max_value=200, value=70)
height = st.sidebar.number_input("Height (in cm)", min_value=100, max_value=250, value=170)
activity_level = st.sidebar.selectbox("Activity Level", ["Low", "Moderate", "High"])
dietary_preference = st.sidebar.selectbox("Dietary Preference", ["Keto", "Vegetarian", "Low Carb", "Balanced"])
fitness_goal = st.sidebar.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"])

# Divider for aesthetics
st.markdown("---")

# Displaying the user's inputted fitness profile
st.markdown("### 🏃‍♂️ My Health Mission")
name = st.text_input("Your good name here please!", " ")

# Button to generate the full health plan
if st.sidebar.button("Design your Health Blueprint"):
    if not age or not weight or not height:
        st.sidebar.warning("Please fill in all required fields.")
    else:
        with st.spinner("💥 Launching your personal wellness journey..."):
            full_health_plan = get_full_health_plan(name, age, weight, height, activity_level, dietary_preference, fitness_goal)

            # Display the generated health plan in the main section
            st.subheader("Your Personalized Health & Fitness Plan")
            st.markdown(full_health_plan.content)

            st.info("This is your customized health and fitness strategy, including meal and workout plans.")

        # Motivational Message
        st.markdown("""
            <div class="goal-card">
                <h4>"Stay Committed, Stay Active!"🏆</h4>
                <p>Persistence pays off! Keep striving, and success will follow."</p>
            </div>
        """, unsafe_allow_html=True)
