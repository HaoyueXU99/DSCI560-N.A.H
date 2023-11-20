css = '''
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
}
.chat-message.user {
    background-color: #386641; /* 猎人绿 */
}
.chat-message.bot {
    background-color: #a7c957; /* 芦笋绿 */
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
  color: #f2e8cf; /* 羊皮纸色 */
}

blockquote {
    margin: 1em 0px 1em -1px;
    padding: 0px 0px 0px 1.2em;
    font-size: 20px;
    border-left: 5px solid #a7c957; /* 黄绿色 */
    background-color: #f2e8cf; /* 羊皮纸色 */
}
blockquote p {
    font-size: 30px;
    color: #386641; /* 猎人绿 */
}
[data-testid=stSidebar] {
    background-color: #a7c957 !important; /* 芦笋绿 */
    color: #f2e8cf; /* 羊皮纸色 */
}
[aria-selected="true"] {
    color: #bc4749; /* 苦甜闪光 */
}    
button {
    color: #386641 !important; /* 猎人绿 */
}
::placeholder {
    color: #6a994e !important; /* 芦笋绿 */
}  
input {
    color: #a7c957 !important; /* 黄绿色 */
}    
</style>


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
