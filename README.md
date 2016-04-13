# Alexa Traffic Time Skill

This skill reads the estimated traffic time based on predefined people and places. It uses the Google Maps Directions API and is built to run on AWS Lambda.

For more information, take a look at my [blog post](https://ewenchou.github.io/blog/2016/04/12/asking-for-traffic/).

## Setup

1. Clone this repository

  ```
  git clone https://github.com/ewenchou/alexa-traffic-time.git
  ```

2. Install requirements locally

  ```
  cd alexa-traffic-time
  pip install -t . -r requirements.txt
  ```

3. Edit `lambda_function.py` and setup the values for:

  * `APP_ID`
  * `GMAPS_API_KEY`
  * `PEOPLE_AND_PLACES`
  * `DEFAULT_PERSON`

4. Create a zip file of the project directory and upload to your AWS Lambda function.
