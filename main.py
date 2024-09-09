#!/usr/bin/env python
import praw
from dotenv import load_dotenv
import os
from openai import OpenAI 
import sys
import time

# user .env file to save your credentials
load_dotenv()

# Extracts user Credentials from env file
username=os.getenv('username')
client_id=os.getenv('client_id')
client_secret=os.getenv('client_secret')
password=os.getenv('password')


class RedditBot:
    def __init__(self, reddit):
        self.reddit = reddit
        self.replied_file = "replied_to.txt"


    #Reddit account data
    def usrInfo(username, client_id, client_secret, password):
        Reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent="testscript",
            username=username,
        )
        
    
        Reddit.read_only = False

        return Reddit

    # Verifies user
    def usrVerify(reddit, username):
        if reddit.user.me() != username:
            sys.exit(1)
        print(reddit.user.me())

    #response generator using chatgpt
    def response(self, prompt, name):
        client = OpenAI(
        api_key=os.getenv("api_key"),
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": f"You are a human using reddit, your mainly task is to roast {name}. Look up all the subreddit where user has replied and sometimes you roast taking those subreddit but not always. And if someone's reply or post is in Hindi, sometimes you will also reply in Hinglish but mostly you reply in english"},
                {"role": "user", "content": prompt},
            ]
        )

        return completion.choices[0].message.content

    #chatgpt checking image of the post 
    def check_image(image):
        client = OpenAI()

        responseImage = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "image_url",
                "image_url": {
                    "url": image,
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )

        return responseImage.choices[0]


    # Gets all the subreddits in the limits of 200 that user has posted/commented
    def get_user_subreddits(self, reddit, username):
        user = reddit.redditor(username)
        subreddits = [] # Use a set to avoid duplicates

        try:
            # Check subreddits where the user has submitted posts
            for submission in user.submissions.new(limit=200):  # Adjust the limit as needed
                subreddits.append(submission.subreddit.display_name)

            # Check subreddits where the user has commented
            for comment in user.comments.new(limit=200):  # Adjust the limit as needed
                subreddits.append(comment.subreddit.display_name)

        except Exception as e:
            print(f"Error fetching data for user {username}: {e}")
        
        return subreddits

    # This is the main function that gathers the information about the post checks the comments and reply to the comment where the bot has been mentioned on reddit
    def check_mentions(self, reddit, userName):
            try:
                mentions = self.reddit.inbox.mentions(limit=10)
                for mention in mentions:
                    if not mention.author.name == "AutoModerator":
                        submission = mention.submission
                        submission_id = mention.submission.id
                        comment_id = mention.id
                        
                        if self.has_already_replied(submission_id, comment_id):
                            print(f"Already replied to: {mention.context}")
                            continue



                        submission.comments.replace_more(limit=None)
                        all_comment = submission.comments.list()
                        postDiscription = submission.selftext

                        mentionTitle = mention.submission.title
                        whoMention = mention.author.name
                        mentionSubreddit = mention.subreddit.display_name
                        mentionText = mention.body
                        mentionUrl = mention.context
                        for commment in all_comment:
                            commentBody = commment.body

                        user_commented = self.get_user_subreddits(reddit=reddit, username=whoMention)
                        prompt = f"""
                        Context:
                        - Post Title: {mentionTitle}
                        - OP: {whoMention}
                        - where OP has been active recently and mostly:{user_commented}
                        - Post Description: {postDiscription}
                        - Subreddit: {mentionSubreddit}
                        - Discussion: {commentBody}
                        - prompt: {mentionText}
                        - Replying to: {whoMention}
                        - url of the post: {mentionUrl}

                        Generate a response that fits this context.
                        """
                        # Rules:
                        # - Bot Personality: {bot_personality}
                        # - Guidelines: {bot_guidelines}
                        # - Image: {image_description}
                        # print(prompt)

                        user_name = whoMention
                    
                        user_name1 = list(user_name)
                        user_name2 = user_name1[2:]
                        user_nameFinal = ''.join(user_name2)
                        ai_response = self.response(prompt=prompt, name=user_nameFinal)
                        print(ai_response)

                        mention.reply(ai_response)
                        mention.mark_read()
                        self.log_replied(submission_id, comment_id)
            except Exception as e:
                print(f"Error fetching mentions: {e}")

            return 0


    # Checks if the post/comment ID is in the log file (Already replied or not)
    def has_already_replied(self, submission_id, comment_id):
        if os.path.exists(self.replied_file):
            with open(self.replied_file, "r") as file:
                replied_ids = file.read().splitlines()
            if comment_id in replied_ids:
                return True
        return False

    # Log the submission and comment IDs to the file (Keeps the log where bot has already replied)
    def log_replied(self, submission_id, comment_id):
        with open(self.replied_file, "a") as file:
            file.write(submission_id + "\n")
            file.write(comment_id + "\n")





def main():
    while True:
        try:
            # Load environment variables
            load_dotenv()

            username = os.getenv('username')
            client_id = os.getenv('client_id')
            client_secret = os.getenv('client_secret')
            password = os.getenv('password')

            # Initialize Reddit instance
            reddit = RedditBot.usrInfo(username, client_id, client_secret, password)

            # Verify user
            RedditBot.usrVerify(reddit, username)

            # Create an instance of the RedditBot class
            bot = RedditBot(reddit)

            # Example: Check mentions and generate a response
            bot.check_mentions(reddit, username)
            
            # Optionally, add a short sleep to prevent rapid looping
            time.sleep(5)  # Adjust as needed

        except KeyboardInterrupt:
            print("Loop interrupted by user.")
            break

if __name__ == "__main__":
    main()



