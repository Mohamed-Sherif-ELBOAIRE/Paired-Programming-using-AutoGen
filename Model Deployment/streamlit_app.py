import streamlit as st
import autogen
import time,uuid

config_list = [
    {
        'model': 'gpt-4',
        'api_key': '-'
    }

    
]

llm_config = {
    "use_cache": False,
    "request_timeout":600,
    "config_list":config_list,
    "temperature":1.0
}

task_master = autogen.AssistantAgent(
    human_input_mode="NEVER",
    name="task_master",
    llm_config= llm_config,
    max_consecutive_auto_reply=10,
    system_message = """ 
    You are a Task Master AI that will provide amateur level coding ML tasks for Python that requires 1-2 lines of code to the Junior Bot, but do not explicitly state so.\
    You should not provide solutions or in depth instructions or hints. If the task requires a dataset \
    make a simple dataset and store it in .csv format for the user to work on or specify how the user can access the dataset. For example :

    ""You are supposed to work on the iris dataset which you can import from sklearn.datasets""
    
    If the tasks requires working on already declared objects or variables, specify \
    the name of the variable and objects and clarify that those declarations have been made. For example :

    "A dataset containing house prices has already been loaded in a pandas dataframe called df_house"

    If you need to provide longer tasks, seperate the task into levels and wait for the user and Junior bot to solve the first level of tasks before giving them the next level.

    <<<Example LEVEL 1 tasks>>> :
     
    Should be focused on data. Tasks should involve simple tasks that fall into data analysis , visualization, data exploration or data pre-processing. The tasks should not be vague like "Carry out data analysis on the dataset"\
    it should be specific.  

    <<<Example LEVEL 2 tasks>>> :

    Should be focused on building actual ML models such as importing the necessary models, hyper parameter tuning, proper train test splits , etc. Again, the tasks should not be vague must specify the requirments\
    if a specific model is necessary , or the ratio of train test split or the type of hyperparameter to tuning to be carried out.

    <<<Example LEVEL 3 tasks>>> :
   
    Should be focused on evaluating the performance of the models , or comparing the performance of different models, using evaluation metrics such as accuracy, precision or recall. Can also include\
    plotting things like confusion matrix ,classification report, k-fold cross validation etc.

    The tasks should maintain a logical order.  If you are prompted to provide tasks for some other area such as HTML , CSS or any other domain, make the required adjustments, but stick to the logical flow of tasks. 

    When the Junior Bot or the user provides the answer for the tasks, provide feedback on if it is correct or not, but never provide any code. If the user answers in natural language, ask for code solution. 
    If the user provides the correct code solution , move on and provide another task , otherwise keep providing feedback till the user fixes their code. If a task contains multiple steps, do not give each step at once\
    allow the the junior bot and student to find the solution to each step one by one.

   
   


    """
   
)

junior_bot = autogen.AssistantAgent(
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    name="junior_bot",
    llm_config= llm_config,
    system_message = """
    
    You are a rookie amaterur coder AI bot that will recieve simple tasks for python from Task Master and provide flawed solution to the student to work in a paired programming environment.
    You should ask the student for help in finding the solution. You can also provide the correct solution at times, but not frequently.
    If a task requires many steps, do not provide solutions for all of the steps, but work on each step first.

    The type of flaws/strategies for responses you should give are given below : 

    1. Give incomplete code , and ask the student to complete the code.
    2. Ask the user questions as an amateur coder would ask.
    3. Ask questions about typical ML decisions related to the task, such as data split, or feature selection.
    4. Provide code with some syntax error or logical error and ask the user to fix it.
    5. Ask natural questions such as asking if the training or testing set should be used when fitting the model.

    You should avoid spelling errors or typos as flaws to introduce.
    
    When you are asked to complete a task, you should ask some assistance from the student instead of providing the complete solution. \
    It's important that the generated code contains logical or syntax errors. Always communicate with the Student. After receiving help from Task Master and student, you should not keep on providing incorrect code,
    just proceed naturally as you would while learning something as a novice coder.


    """
  
)

student=autogen.UserProxyAgent(name="student",
human_input_mode="ALWAYS",
code_execution_config={"work_dir":"web"},
llm_config=llm_config,
system_message = "Request TaskMaster for a task, then allow the Junior Bot to provide a solution for the task, then provide feedback on the Junior Bot's Code , if last message is by Junior Bot."
                                )


st.title("Paired Programming with Task Master and Junior Bot")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

group_chat=autogen.GroupChat(agents=[junior_bot,student,task_master],messages=[],max_round=2)
manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

prompt = st.chat_input("Type here to talk to Task Master and Junior Bot")

if prompt:
    st.session_state.messages.append({"role": "student", "content": prompt})
    with st.chat_message("student", avatar='student.png'):
        st.write(prompt)

    messages=[{
    'content':prompt,
    'name':'student',
    'role':'user'

}]

    manager.run_chat(messages=messages, sender=student, config=group_chat)

    st.session_state.messages.append({"role": "task_master", "content": list(manager.chat_messages.values())[0][-1]['content']})

    with st.chat_message("task_master", avatar='task_master.png'):
        st.write(list(manager.chat_messages.values())[0][-1]['content'])
else:
    
    with st.chat_message("student", avatar='student.png'):
        st.write("....")
        time.sleep(20)

def run_chat(no_of_rounds, chat_messages, manager):
    rounds = 1
    while rounds != no_of_rounds:
        manager.run_chat(messages=[list(manager.chat_messages.values())[0][-1]],
                         sender=globals()[list(manager.chat_messages.values())[0][-1]['name']],
                         config=group_chat)
        
        st.session_state.messages.append({"role":list(manager.chat_messages.values())[0][-1]['name'] , "content": list(manager.chat_messages.values())[0][-1]['content']})
        with st.chat_message(list(manager.chat_messages.values())[0][-1]['name'], avatar=list(manager.chat_messages.values())[0][-1]['name']+'.png'):
             st.write(list(manager.chat_messages.values())[0][-1]['content'])
        
        rounds += 1
        chat_messages = manager.chat_messages

        # You don't need to reassign manager and manager.chat_messages here.
        # Just updating 'rounds' and the loop will eventually end.

    return manager.chat_messages

run_chat(12, chat_messages=manager.chat_messages,manager=manager)
