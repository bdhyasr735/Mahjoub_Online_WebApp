# coding: utf-8
# 📂 apps/services/product_ident_mutation.graphql.py

UPDATE_PRODUCT_IDENTIFICATION_MUTATION = """
mutation UpdateProductIdentification(
  $id: ID!, 
  $data: IdentificationInput!
) {
  updateProductIdentification(id: $id, data: $data)
}
"""
