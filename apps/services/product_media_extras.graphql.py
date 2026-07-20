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
      }
    }
  }
}
"""

MANAGE_MEDIA_AND_EXTRAS_MUTATION = """
mutation ManageMediaAndExtras(
  $productId: ID!,
  $slug: String!,       # تم إضافة حقل الرابط هنا
  $imageIds: [ID!]!,
  $tags: [String!]!,
  $collectionIds: [String!]!
) {
  # تحديث الرابط (Slug) ضمن معلومات المنتج
  updateProductInfo(id: $productId, updateProductInfoInput: { slug: $slug }) {
    qid
  }

  # تحديث قائمة صور المنتج
  updateProductImages(id: $productId, data: $imageIds) {
    qid
  }

  # تحديث وسوم المنتج
  updateProductInfo(id: $productId, updateProductInfoInput: { tags: $tags }) {
    qid
  }

  # تحديث تصنيفات المنتج
  updateProductCollection(collectionIds: $collectionIds) {
    qid
  }
}
"""
