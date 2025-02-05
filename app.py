import streamlit as st
from chat_interface import ChatInterface
from chatbot_config import ChatbotConfig

def main() -> None:
    """Main entry point of the application"""
    # Initialize configuration
    config = ChatbotConfig()
    
    # Setup sidebar configuration
    config.setup_sidebar()
    
    # Initialize chat interface
    chat_interface = ChatInterface(config)
    
    # Setup UI
    chat_interface.setup_ui()
    
    # Initialize session state
    chat_interface.initialize_session_state()
    
    # Get user input
    user_question = st.text_input("Ask a question:")
    
    # Process user input and display response
    if user_question:
        # Get the response and query results
        result = chat_interface.process_user_input(user_question)
        
        # Check if the response contains SQL query results
        if isinstance(result, dict) and 'type' in result:
            if result['type'] == 'tour_query':
                # Display the generated SQL query in an expander
                # with st.expander("View Generated SQL Query"):
                #     st.code(result['query'], language='sql')
                
                # Display the results in a table if there are any
                # if result['results']:
                #     st.write("Query Results:")
                #     st.dataframe(result['results'])
                
                # Display the natural language response
                st.write("Chatbot:", result['response'])
                
            elif result['type'] == 'error':
                st.error(f"Error: {result['error']}")
            else:
                st.write("Chatbot:", result['response'])
        else:
            # Display regular chat response
            st.write("Chatbot:", result)
        
        # Display chat history
        if st.session_state.chat_history:
            st.divider() 
            st.caption("Chat History")
            
            chat_container = st.container()
            
            with chat_container:
                for msg in st.session_state.chat_history:
                    with st.chat_message("user", avatar="👤"):
                        if "```" in msg.human:
                            st.markdown(msg.human)
                        else:
                            st.write(msg.human)
                    
                    with st.chat_message("assistant", avatar="🤖"):
                        if "```" in msg.AI:
                            st.markdown(msg.AI)
                        else:
                            st.write(msg.AI)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("Clear History", type="secondary"):
                        st.session_state.chat_history = []
                        st.rerun()



if __name__ == "__main__":
    main()
