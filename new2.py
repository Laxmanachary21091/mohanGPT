import streamlit as st  # ✅ Import first
import google.generativeai as genai
import random
import requests
from fpdf import FPDF
import base64

# ✅ Set your API key here
genai.configure(api_key="AIzaSyBtpMgteEECx3LKR_hO6kCJswu6zPNEzzg")

# ✅ First, configure the page (Must be the first Streamlit command)
st.set_page_config(page_title="Flavour Fusion:AI-Driven Recipe Blogging", page_icon="🍽", layout="centered")

# ✅ Use title for the app
st.title("🍽 Flavour Fusion:AI driven Recipe Blogging")

# ✅ Function to set background
def set_bg(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# ✅ Call the function with the image file
set_bg("back2.jpg")  # Ensure the image is in the same directory

# ✅ Predefined food jokes
jokes = [
    "🍅 Why did the tomato turn red? Because it saw the salad dressing!",
    "🐟 I'm on a seafood diet. I see food and I eat it!",
    "🥚 Why don’t eggs tell jokes? Because they might crack up!",
    "💀 What’s a skeleton’s least favorite meal? Spare ribs!"
]

# ✅ Function to check if the input is related to food using Gemini AI
def is_food_related(topic):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(f"""
        The user has entered the topic: "{topic}".  
        Determine if this topic is related to food, cooking, or recipes.  
        Respond ONLY with 'Yes' or 'No' (without any extra text or explanation).  
        If it is a food item, say 'Yes'.  
        If it is unrelated (like a story, technology, or random words), say 'No'.  
        """)

        answer = response.text.strip().lower()
        return answer == "yes"
    except Exception as e:
        st.error(f"⚠ Error checking topic relevance: {e}")
        return False

# ✅ Function to generate a recipe with nutrition info
def get_gemini_recipe(topic, word_count=300, blog_style="Simple and clear"):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(f"""
        Create a detailed recipe blog post for "{topic}" in a {blog_style} style.
        Include ingredients, step-by-step instructions, preparation time, cooking time, servings, side dish pairings, other recipe suggestions,tips and funfacts.
        Keep it within {word_count} words.
        
        Also, generate a *nutrition breakdown* for the recipe including:
        - Calories per serving
        - Macronutrients (Carbs, Protein, Fats)
        - Key Micronutrients (Vitamins & Minerals)
        
        *Embed the nutrition breakdown* naturally *at the end of the blog content* instead of separating it.
        """)

        return response.text if response else "Error: No response from AI"
    except Exception as e:
        return f"⚠ Error generating recipe: {e}"

# ✅ Function to find a YouTube cooking video for the topic
def find_best_youtube_video(query):
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+recipe"
    return search_url

# ✅ Function to generate a PDF from the recipe text
def generate_pdf(recipe_text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, recipe_text)
    pdf_file = "recipe.pdf"
    pdf.output(pdf_file)
    return pdf_file

# ✅ Streamlit UI
st.write("💡 Enter a dish name and get a full recipe instantly!")

# ✅ Input fields
topic = st.text_input("🥑 Enter a recipe topic (e.g., Chicken Biryani, Tomato Soup)🔍", "")
word_count = st.slider("📖 Select word count for the recipe:", min_value=300, max_value=1200, value=400, step=50)
blog_style = st.selectbox("🎨 Choose blog style:", ["Simple and clear", "Professional and detailed", "Fun and engaging"])

if st.button("🍳 Generate Recipe"):
    if topic:
        with st.spinner("✨ Generating your recipe... Please wait!"):
            if is_food_related(topic):
                joke = random.choice(jokes)
                st.info(f"😂 {joke}")

                with st.spinner(""):
                    result = get_gemini_recipe(topic, word_count, blog_style)
                    if "Error" in result:
                        st.error(result)
                    else:
                        st.success("🎉 Recipe Generated Successfully!")
                        st.markdown("## 🍽 Your AI-Generated Recipe")
                        st.write(result)

                        # ✅ Generate Links
                        youtube_url = find_best_youtube_video(topic)
                        swiggy_url = f"https://www.swiggy.com/search?q={topic.replace(' ', '%20')}"
                        pdf_file = generate_pdf(result)
                        with open(pdf_file, "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

                        # ✅ Display useful links
                        st.markdown("---")
                        st.markdown("### 🔗 Useful Links")
                        st.markdown(f"[🎥 Watch Recipe on YouTube]({youtube_url})", unsafe_allow_html=True)
                        st.markdown(f"[🍔 Order on Swiggy]({swiggy_url})", unsafe_allow_html=True)
                        st.markdown(f"[📄 Download Recipe PDF](data:application/pdf;base64,{base64_pdf})", unsafe_allow_html=True)
            else:
                st.error("❌ This topic is not related to food recipes. Please enter a valid food topic.")
    else:
        st.error("❌ Please enter a recipe topic.")