# Coresender Python SDK

This is the officially supported Python library for [Coresender](https://coresender.com). It allows you to quickly and easily integrate with our API and improve your email deliverability.

### Prerequisites

* Python version 3.6+
* The Coresender service. You can start with a free 100 emails/month developer plan and move to one of our [pricing plans](https://coresender.com/pricing) when you're done.

### Installation

Run the following command to get started: 

```bash
python3 -m pip install coresender
```

### Usage

Here's how to send an email using the SDK:

```python
import asyncio
import uuid

import coresender

async def main():
    coresender.init(
        sending_account_id='<<INSERT CORESENDER SENDING ACCOUNT ID>>',
        sending_account_key='<<INSERT CORESENDER SENDING ACCOUNT API KEY>>',
        # debug=True # if True, then show some logs on stderr
    )

    # EXAMPLE 1 – Recommended
    
    rq = coresender.SendEmail()
    custom_id = str(uuid.uuid4())
    rq.add_to_batch(
        from_email='sender@example.com',
        from_name='sender',
        to_email='recipient-1@example.net',
        to_name='Recipient-1',
        subject='Coresender test ' + custom_id,
        body_text='Hello,\nWorld!',
        body_html='<strong>Hello</strong>,<br>World!',
        custom_id=str(custom_id),
        track_opens=True,
        track_click=True
    )

    custom_id = str(uuid.uuid4())
    rq.add_to_batch(
        from_email='sender@example.com',
        from_name='sender',
        to_email='recipient-2@example.net',
        to_name='Recipient-2',
        subject='Coresender test ' + custom_id,
        body_text='Hello,\nWorld!',
        body_html='<strong>Hello</strong>,<br>World!',
        custom_id=str(custom_id),
        track_opens=True,
        track_click=True
    )
    rsp = await rq.execute()
    for i in rsp:
         print(i)


    # Example 2 – For the simplest needs
    
    custom_id = str(uuid.uuid4())
    rsp = await rq.simple_email(
        from_email='sender@example.com', 
        to_email='recipient-1@example.net',
        subject='Coresender test ' + custom_id,
        body='<strong>Hello</strong>,<br>World!',
        body_type=coresender.BodyType.html
    )
    print(rsp)
    

if __name__ == '__main__':
    asyncio.run(main())

```

### Environment variables

Instead of putting sending account credentials directly in the code, you may want to put them in your environment variables:

```shell
CORESENDER_SENDING_API_ID=<<INSERT CORESENDER SENDING ACCOUNT ID>>
CORESENDER_SENDING_API_KEY=<<INSERT CORESENDER SENDING ACCOUNT API KEY>>
```

The library will detect it automatically and use the credentials stored as environment variables.

### Response

The result of a method call is, by default, a domain object.
Every response object has `http_status` property that contains API HTTP response code. Other properties depend on the method you use.

#### `SendEmail.execute`

The response is an instance of `responses.SendEmail`. Because this method allows for sending many emails with one API request, the `SendEmail.all_accepted` property lets you quickly check if all messages were accepted. If its value is `false` it means you have to further check for rejected messages.
    
`responses.SendEmail` is also an iterator that contains information about the status (and possible errors) of every message from the batch. Items are instances of `responses.SendEmailResponse`, containing data returned by the API.

#### `SendEmail.simple_email`

As this method allows for sending just one email, without batching, the response is simply an instance of `responses.SendEmailResponse`.

# Debugging

For debug purposes there is a flag in `Coresender.init` method (look at Usage section above). If you enable `debug`, the library will print out logs to `STDERR` by default. You can configure it further by fetching `coresender` log handler:

```python
import logging
logger = logging.getLogger('coresender')
```

For more information about loggers, take a look at official documentation of the [`logging` module](https://docs.python.org/3/library/logging.html).

# Development

For installing dependencies use [Pipenv](https://github.com/pypa/pipenv):

```shell script
pipenv install --dev
pipenv shell
```

### Contribute

The Coresender PHP SDK is an open-source project released under MIT license. We welcome any contributions!

You can help by:
* Writing new code
* Creating issues if you find problems
* Helping others with their issues
* Reviewing PRs

