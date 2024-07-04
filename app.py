import os
import random
import asyncpraw  # https://asyncpraw.readthedocs.io/en/stable/getting_started/quick_start.html
import anthropic
#from google.colab import userdata

# Set variables
# anthropic_api_key = userdata.get('anthropic_api_key')
# anthropic_org_id = userdata.get('anthropic_org_id')
# os.environ["ANTHROPIC_API_KEY"] = userdata.get('anthropic_api_key')
# reddit_client_id = userdata.get('reddit_client_id')
# reddit_client_secret = userdata.get('reddit_client_secret')
anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
anthropic_org_id = os.environ["ANTHROPIC_ORG_ID"]
reddit_client_id = os.environ["REDDIT_CLIENT_ID"]
reddit_client_secret = os.environ["REDDIT_CLIENT_SECRET"]


# Reddit stuff

# Create a reddit object.
reddit = asyncpraw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent='script:reddit_stream:v1.0 (by /u/bliiir)',
)

# Get a subreddit object for /r/scams.
subreddit = await reddit.subreddit('scams', fetch=True)

# Fetch a number of posts and their comments.
posts = {}
async for post in subreddit.hot(limit=100):  # "hot" to "new" or "top"
    await post.load()
    posts[post.id] = {}
    posts[post.id]['title'] = post.title
    posts[post.id]['url'] = post.url
    posts[post.id]['selftext'] = post.selftext
    for comment in post.comments.list():
      try:
        posts[post.id]['comments'].append(comment.body)
      except:
        continue

# pick a random post
test_id = random.choice(list(posts.keys()))


# Anthropic stuff

# Create an Anthropic client.
client = anthropic.Anthropic()

# Create the prompt.
prompt = f"""
You are a moderator bot in the r/scams subreddit. The subreddit history looks like this:

[HISTORY START]
{posts}
[HISTORY END]

When given this post:

[NEW POST START]
{posts[test_id]}
[NEW POST END]

You output only a single word from the LIST below to identify the type of scam in question based on the history. If it is not a scam, just say !not_scam:

[START LIST]
!advancefee
!advance
!advance
!airdrop
!blackmail
!brushing
!calendar
!car
!cartel
!escort
!courier
!crypto
!deaththreat
!debt
!fakecheck
!fakecheque
!fakepayment
!google
!googlevoice
!influencer
!instagram
!iphone
!mail
!muse
!artist
!mlm
!parcelmule
!pet
!puppy
!pigbutchering
!pin
!verify
!verification
!ps5
!recovery
!refund
!rental
!review
!romance
!sextortion
!Skype
!steam
!sugar
!task
!techsupport
!tax
!irs
!cra
!hmrc
!underage
!wrongnumber
!Mandy
[END LIST]
"""

# Ask Claude.
message = client.messages.create(
  model="claude-3-5-sonnet-20240620",
  max_tokens=16,
  # max_tokens=1024,
  messages=[
    {
      "role": "user",
      "content": prompt
    }
  ]
)



# Look at the result.
print(f"Input was:\n{posts[test_id]['title']}\n")
print(f"{posts[test_id]['selftext']}\n\n")
print(f"Claude says: {message.content}\n")
