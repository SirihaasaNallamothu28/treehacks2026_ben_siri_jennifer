def search(technical_interests: list[str], medical_interests: list[str]) -> list[str]:
    '''
    This function takes in a list of technical interests and a list of medical interests, and triggers an agentic search in our Elastic Vector Database
    
    :param technical_interests: A list of technical interests, such as "CNN", "ML", "NLP", "3D transformers, "diffusion", etc
    :type technical_interests: list[str]
    :param medical_interests: A list of medical interests, such as "cancer", "cardiology", "neuroscience", "arthritis", etc
    :type medical_interests: list[str]
    :return: A list of raw JSON strings, each containing a paper abstract and metadata, such as title, authors, journal, DOI, etc
    :rtype: list[str]
    '''

    # TODO: This function calls the Elastic Agentic Search Agent, which is responsible for formulating a search query based on the provided technical and medical interests, executing the search against the Elastic Vector Database, determining which papers are the most relevant based on the interests, and returning the "source" text of those queries.

    return []

