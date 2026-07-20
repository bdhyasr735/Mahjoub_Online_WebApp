# coding: utf-8
# 📂 apps/services/fetch_collections_data.graphql.py

GET_ALL_COLLECTIONS_QUERY = """
query Data($input: GetAllCollectionsInput) {
  findAllCollections(input: $input) {
    data {
      qid
      app
      title
      slug
      handle
      description
      operation
      productCount
      products {
        
      }
      image {
        
      }
      condations {
        
      }
    }
    success
    message
    pagination {
      
    }
  }
}
"""
