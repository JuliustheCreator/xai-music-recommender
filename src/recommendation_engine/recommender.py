"""
A module for generating personalized music recommendations.

This module contains functions for fetching the user's top tracks from Spotify, 
generating music recommendations based on those tracks, and fetching explanations for the recommendations.

Functions:
    get_recommendations: Fetch the user's top tracks, generate recommendations, and fetch explanations.
"""

from spotify.api import fetch_user_top_tracks, fetch_track_recommendations, fetch_top_artists
from utils.langchain_utils import RecommendationLLM, ExplanationLLM  
from flask import session


###########################
## Recommendation Engine ##
###########################


def get_recommendations():
    """
    Fetches the user's top tracks from Spotify, generates recommendations based on those tracks,
    and then fetches explanations for those recommendations.

    Returns:
        
            recommendations (list): A list of recommended songs.
            explanations (list): A list of explanations for the recommendations.
    """

    if not session.get('access_token'):
        return None, "Access token is not available. Please log in."

    access_token = session['access_token']

    top_tracks = fetch_user_top_tracks(access_token, limit = 20, time_range = 'long_term')
    top_artists = fetch_top_artists(access_token, limit = 20, time_range = 'long_term')
    candidates = fetch_track_recommendations(access_token, fetch_user_top_tracks(access_token), fetch_top_artists(access_token))

    # print("Top Tracks: ", top_tracks)
    # print("Top Artists: ", top_artists)
    # print("Songs: ", candidates)

    if not top_tracks: return None, "Failed to fetch top tracks from Spotify."
    if not top_artists: return None, "Failed to fetch top artists from Spotify."
    if not candidates: return None, "Failed to fetch recommendations from Spotify."

    try:
        recommendationLLM = RecommendationLLM()
        explanationLLM = ExplanationLLM()

        recommendations = explanationLLM(
            recommendationLLM(top_tracks, top_artists, candidates)
            )
    
    except Exception as e:
        return None, f"Error processing recommendations: {str(e)}"

    return recommendations