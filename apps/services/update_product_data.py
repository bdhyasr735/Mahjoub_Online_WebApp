# coding: utf-8
# 📂 apps/services/update_product_data.py

UPDATE_PRODUCT_MUTATION = """
mutation UpdateProductEverything(
  $id: String!,
  $info: UpdateProductInfo!,
  $pricing: PricingInput!,
  $dims: DimensionsInput!,
  $weight: WeightInput!,
  $ident: IdentificationInput!,
  $desc: String!,
  $collection_ids: [String!],
  $removed_images: [String!],
  $new_images: [String!],
  $variants: [VariantInput!]
) {
  updateProductInfo(id: $id, updateProductInfoInput: $info) { success message }
  updateProductPricing(id: $id, pricing: $pricing) { success message }
  updateProductDimensions(id: $id, data: $dims) { success message }
  updateProductWeight(id: $id, data: $weight) { success message }
  updateProductIdentification(id: $id, data: $ident) { success message }
  updateProductDescription(id: $id, data: $desc) { success message }
  updateProductCollections(id: $id, collectionIds: $collection_ids) { success message }
  updateProductVariants(id: $id, variants: $variants) { success message }
}
"""
