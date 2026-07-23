# coding: utf-8
# 📂 apps/services/fetch_product_data.graphql.py

GET_PRODUCT_DETAIL_QUERY = """
query($qid: String!) {
    findProductByQid(qid: $qid) {
        success
        message
        data {
            qid
            title
            slug
            description
            status
            quantity
            pricing {
                price
                compareAtPrice
            }
            images {
                _id
                fileUrl
            }
            collections {
                qid
                title
                slug
            }
            variants {
                _id
                quantity
                pricing {
                    price
                    compareAtPrice
                }
            }
        }
    }
}
"""
