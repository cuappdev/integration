from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup


BASE_URL = environ["VOLUME_BACKEND_URL"]
URL_PARAMS_ARTICLES = "?query=" + parse.quote("query {getAllArticles{ id title publicationSlug } }")  # url encoding
URL_PARAMS_ARTICLES_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """ query {
        getAllArticles{
          id
          articleURL
          date
          imageURL
          publication{
            bio
            profileImageURL
            rssName
            slug
            shoutouts
            websiteURL
            contentTypes
          }
          publicationSlug
          shoutouts
          title
          nsfw
          isTrending
          trendiness
        }
      }
      
"""
)
URL_PARAMS_PUBLICATIONS_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """query {
      getAllPublications {
        id
        backgroundImageURL
        bio
        bioShort
        name
        profileImageURL
        rssName
        slug
        shoutouts
        websiteURL
        contentTypes
        mostRecentArticle {
          title
        }
        numArticles
        socials {
          URL
          social
        }
        contentTypes
      }
    }
"""
)


def all_article_fields_non_empty(r):
    response = r.json()
    try:
        return all(response["data"]["getAllArticles"])
    except:
        raise Exception(f'{response}')


def all_publication_fields_non_empty(r):
    response = r.json()
    return all(response["data"]["getAllPublications"])


tests = [
    Test(name="Articles query", request=Request(method="GET", url=BASE_URL + URL_PARAMS_ARTICLES)),
    Test(
        name="Fields that should never be empty for articles query",
        request=Request(method="GET", url=BASE_URL + URL_PARAMS_ARTICLES_NON_EMPTY),
        callback=all_article_fields_non_empty,
    ),
    Test(
        name="Fields that should never be empty for publications query",
        request=Request(method="GET", url=BASE_URL + URL_PARAMS_PUBLICATIONS_NON_EMPTY),
        callback=all_publication_fields_non_empty,
    ),
]

volume_tests = TestGroup(application=Application.VOLUME, name="Volume", tests=tests)
