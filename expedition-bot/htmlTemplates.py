css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}

blockquote {
    margin: 1em 0px 1em -1px;
    padding: 0px 0px 0px 1.2em;
    font-size: 20px;
    border-left: 5px solid rgb(230, 234, 241);
    # background-color: rgb(129, 164, 182);
}
blockquote p {
    font-size: 30px;
    color: #FFFFFF;
}
[data-testid=stSidebar] {
    background-color: rgb(129, 164, 182) !important;
    color: #FFFFFF;
}
[aria-selected="true"] {
    color: #000000;
}    
button {
    color: rgb(129, 164, 182) !important;
}
::placeholder {
    color: rgb(129, 164, 182) !important;
}  
input {
    color: #115675 !important;
            
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/0c/Chatbot_img.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
