# coding: utf-8
# 📂 apps/services/product_media_extras.graphql.py

PRODUCT_MEDIA_EXTRAS_QUERY = """
query GetProductMediaAndExtras($qid: String!) {
  findProductByQid(qid: $qid) {
    data {
      slug        # حقل الرابط (Slug)
      images {
        _id
        fileUrl
      }
      tags
      collections {
        qid
        title
        slug
      }
    }
  }
}
"""

MANAGE_MEDIA_AND_EXTRAS_MUTATION = """
mutation ManageMediaAndExtras(
  $productId: ID!,
  $slug: String!,       
  $removedImages: [String!],
  $newImages: [String!],
  $tags: [String!]!,
  $collectionIds: [String!]!
) {
  # تحديث الرابط (Slug)
  updateProductInfo(id: $productId, updateProductInfoInput: { slug: $slug }) {
    success message
  }

  # تحديث الصور (إزالة وإضافة)
  updateProductImages(id: $productId, removedImages: $removedImages, newImages: $newImages) {
    success message
  }

  # تحديث وسوم المنتج
  updateProductInfo(id: $productId, updateProductInfoInput: { tags: $tags }) {
    success message
  }

  # تحديث التصنيفات
  updateProductCollections(id: $productId, collectionIds: $collectionIds) {
    success message
  }
}
"""
