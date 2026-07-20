# coding: utf-8
# 📂 apps/services/product_media_extras.graphql.py

PRODUCT_MEDIA_EXTRAS_QUERY = """
query GetProductMediaAndExtras($qid: String!) {
  findProductByQid(qid: $qid) {
    data {
      images {
        _id
        fileUrl
      }
      tags
      collections {
        qid
        title
      }
    }
  }
}
"""

MANAGE_MEDIA_AND_EXTRAS_MUTATION = """
mutation ManageMediaAndExtras(
  $productId: ID!,
  $imageIds: [ID!]!,
  $tags: [String!]!,
  $collectionIds: [String!]!
) {
  updateProductImages(id: $productId, data: $imageIds) {
    qid
  }

  updateProductInfo(id: $productId, updateProductInfoInput: { tags: $tags }) {
    qid
  }

  updateProductCollection(collectionIds: $collectionIds) {
    qid
  }
}
"""
