# coding: utf-8
# 📂 apps/services/update_product_data.graphql.py

UPDATE_PRODUCT_MUTATION = """
mutation UpdateProductEverything(
  $id: String!,
  $info: UpdateProductInfo!,
  $pricing: PricingInput!,
  $dims: DimensionsInput!,
  $weight: WeightInput!,
  $ident: IdentificationInput!,
  $desc: String!,
  $collections: [String!],
  $images: [ImageInput!],
  $variants: [VariantInput!]
) {
  updateProductInfo(id: $id, updateProductInfoInput: $info) { success }
  updateProductPricing(id: $id, pricing: $pricing) { success }
  updateProductDimensions(id: $id, data: $dims) { success }
  updateProductWeight(id: $id, data: $weight) { success }
  updateProductIdentification(id: $id, data: $ident) { success }
  updateProductDescription(id: $id, data: $desc) { success }
  updateProductCollections(id: $id, collectionIds: $collections) { success }
  updateProductImages(id: $id, images: $images) { success }
  updateProductVariants(id: $id, variants: $variants) { success }
}
"""
