import streamlit as st
from iron_bars import  process_stock
from pdf_report import generate_pdf_report
import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv
import bcrypt
from streamlit_authenticator.utilities.hasher import Hasher
load_dotenv()


# Credentials dict in exact format required by v0.4.2
credentials = {
    "usernames": {
        "user1": {"name": "User1", "password": os.getenv("PASSWORD_USER1")},
        "user2": {"name": "User2", "password": os.getenv("PASSWORD_USER2")},
        "user3": {"name": "User3", "password": os.getenv("PASSWORD_USER3")},
        "user4": {"name": "User4", "password": os.getenv("PASSWORD_USER4")},
        "user5": {"name": "User5", "password": os.getenv("PASSWORD_USER5")},
    }
}

# Check if any passwords are missing
for user, info in credentials["usernames"].items():
    if info["password"] is None:
        st.error(f"Missing password for {user}. Set it in your .env or Heroku config.")
        st.stop()

# Create the authenticator
authenticator = stauth.Authenticate(
    credentials,
    cookie_name="my_app_cookie",
    key="my_signature_key",
    cookie_expiry_days=1
)

# Show login
name = authenticator.login(location="main")

def run_app():
    st.set_page_config(layout="wide")
    st.title("JRCL's Iron Bar Cutting Optimization Tool")
    st.write("Optimize the cutting of iron bars to minimize waste based on your requirements.") 
    input_col,output_col=st.columns(2)
    with input_col:
      st.header("Input Requirements")
      client_name=st.text_input("Client Name")
      req_count = int(st.number_input("How many different stock types do you have?", min_value=1, value=1, step=1))
      stock_requirements=[]
      results=[]
      for i in range(req_count):
        st.markdown(f"**Stock Type {i+1}**")
        col1,col2=st.columns(2)
        with col1:
           stock_length=st.number_input(f"Stock Length (meters) for type {i+1}",min_value=0.1,value=12.0,step=0.5,key=f"stock_len_{i}")
        with col2:
           stock_diameter=st.selectbox(f"Stock Diameter (mm) for type {i+1}",options=[8,10,12,16,20,25,32],index=3,key=f"stock_dia_{i}")
        piece_count=int(st.number_input(f"How many different required lengths for stock type {i+1}?",min_value=1,value=1,step=1,key=f"piece_count_{i}"))

        requirements=[]
        for j in range(piece_count):
         pcol1,pcol2=st.columns(2)
         with pcol1:
            length=st.number_input(f"Length #{j+1}(m) of stock type #{i+1}",min_value=0.01,value=1.0,step=0.01,key=f"len_{i}_{j}")
         with pcol2:
          qty = st.number_input(f"Quantity for piece {j+1} of stock type {i+1}",min_value=1,value=1,step=1,key=f"qty_{i}_{j}")
          requirements.append((length,qty))
        stock_requirements.append({"stock_length":stock_length,
                                    "stock_diameter":stock_diameter,
                                    "requirements":requirements})
        print(stock_requirements) 
      optimize_button = st.button("Optimize Cutting Plan")

      with output_col:
            st.header("Optimization Results")

      if optimize_button:
            st.subheader(f"Cutting Plan for {client_name}")
            
            for idx, stock in enumerate(stock_requirements):
              stock_length = stock["stock_length"]
              stock_diameter = stock["stock_diameter"]
              requirements = stock["requirements"]

              st.subheader(f"Stock Type {idx+1}: Length {stock_length}m, Diameter {stock_diameter}mm")

              result = process_stock(stock_length, requirements, diameter=stock_diameter)
              results.append(result)

              st.markdown(f"**No. of Bars to Order:** {result['bars_used']}")
              st.markdown(f"**Total Weight of Bars:** {result['total_weight_used'] + result['total_weight_wasted']:.2f} kg")
              st.markdown(f"**Utilized Weight:** {result['total_weight_used']:.2f} kg")
              st.markdown(f"**Total Waste in metre:** {result['total_waste']:.2f} meters")
              st.markdown(f"**Total Weight Wasted:** {result['total_weight_wasted']:.2f} kg")
              st.markdown(f"**Percentage Weight Loss due to Waste:** {result['percent_loss']:.2f}%")

              st.markdown("**Cutting Plans: for each bar (grouped):**")
              for plan, count in result['plan_counter'].items():
                cuts_str = ", ".join(f"{cut:.2f}" for cut in plan)
                waste = stock_length - sum(plan)
                st.write(f"- {count} bar(s): [{cuts_str}] | Waste: {waste:.2f} m")

              if result['unfulfilled_pieces'] > 0:
                st.warning(f"Unfulfilled pieces: {result['unfulfilled_pieces']} (cannot fit in bars)")
            pdf_buffer = generate_pdf_report(client_name, stock_requirements, results)
            st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name=f"{client_name}_iron_report.pdf",
            mime="application/pdf"
        )
           
# Check login status
if st.session_state.get("authentication_status"):
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome {st.session_state['name']} 👋")
    run_app()

    # 🔽 YOUR APP CODE HERE
    st.write("Your private app content goes here")

elif st.session_state.get("authentication_status") is False:
    st.error("Username or password is incorrect")

elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password")
    

          