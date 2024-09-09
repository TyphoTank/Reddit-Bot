# Reddit-Bot
Bot that replies automatically to the comment where it has been mentioned.

It constatntly checks if it has been mentioned somewhere or not. If it is mentioned somewhere in the reddit it checks where it is mentioned and checks all the comments to get context, OP name, Post Title, Post discription, and many more and then it sends those details to chatgpt through openai's API, Based on the personality given to gpt it responds to that which is then posted to reddit and a log file saves all that to keep recordes.


## Credentials

Make .env file and put your credentials in there
match the variable name in your .env file

```python
username=os.getenv('username')
client_id=os.getenv('client_id')
client_secret=os.getenv('client_secret')
password=os.getenv('password')
```

## More

I have to add image of reddit post in the context but i keep procastinating to figure it out. It would be great for me if anyone would help me out.

## License

[MIT](https://choosealicense.com/licenses/mit/)
