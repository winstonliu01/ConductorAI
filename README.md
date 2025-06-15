# Largest Number Extractor from PDF

This tool downloads a local PDF and finds the largest number inside it.
It will display two largest numbers. The first one will only include digits.
The second one will account for some natural language processing for the 
quantifiers. It will not account for conversions for values displayed in charts.

Currently, this program only supports one local PDF file. To run the tool 
successfully, the file will need to be present locally in the same directory.
Additionally, the PDF_PATH environmental variable will need to be updated in 
the Dockerfile. For the given PDF file, this has already been accounted for.

This project uses an object oriented design where we have two classes: 
Document and Page. The Document will have a variable called pages which will
contain a list of Page objects. Inside the Page object is where we handle 
majority of the data cleaning and store data related to the maximum number for
each page.


## Run the commands inside the terminal

1.  Clone the Git repository and go into its directory
    ```
    git clone ConductorAI
    cd ConductorAI
    ```

2.  Build the Docker image
    ```
    docker build -t largest-number-finder .
    ```

3.  Run the Docker Container 
    Note: Please only use the first command. The second command will
    include a lot of debug commands causing the application to run more
    than a minute.
    ```
    docker run --rm largest-number-finder
    docker run --rm -e LOG_LEVEL=DEBUG largest-number-finder
    ```

4.  View the output in the terminal. 
    Right now, we have set the output just as print statements in the terminal.
    But because we aren't logging it, it'll be the line that does not include
    additional attributes such as time stamp and level. We have set INFO log 
    levels for certain points in the program, including when pages have been 
    processed.

### Initial Problem

[Here is a large pdf document](https://www.saffm.hq.af.mil/Portals/84/documents/FY25/FY25%20Air%20Force%20Working%20Capital%20Fund.pdf?ver=sHG_i4Lg0IGZBCHxgPY01g%3d%3d). We want to find the largest number in this document. The unit is not important (could be dollars, years, pounds, etc), we're just looking for the greatest numerical value in the document.

For a bonus challenge if you have time, take natural language guidance from the document into consideration. For example, where the document states that values are listed in millions, a value of 3.15 would be considered to be 3,150,000 instead of 3.15.
