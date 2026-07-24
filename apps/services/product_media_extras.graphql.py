# coding: utf-8
# 📂 apps/services/product_media_extras.graphql.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient
import base64
import os


# ============================================================
# 📋 QUERIES - استعلامات الوسائط
# ============================================================

# 1️⃣ جلب وسائط المنتج
GET_PRODUCT_MEDIA_QUERY = """
query GetProductMedia($qid: String!) {
    findProductByQid(qid: $qid) {
        id
        qid
        title
        images {
            _id
            fileUrl
            title
            description
            mimetype
            sizeInKB
            sizeInMB
            createdAt
        }
        media {
            _id
            fileUrl
            title
            description
            type
            mimetype
            sizeInKB
            sizeInMB
            createdAt
        }
    }
}
"""

# 2️⃣ جلب وسائط الفاريانت
GET_VARIANT_MEDIA_QUERY = """
query GetVariantMedia($variantQid: String!) {
    findVariantById(variantQid: $variantQid) {
        id
        qid
        name
        images {
            _id
            fileUrl
            title
            description
            mimetype
            sizeInKB
            sizeInMB
        }
        media {
            _id
            fileUrl
            title
            description
            type
            mimetype
            sizeInKB
            sizeInMB
        }
    }
}
"""

# 3️⃣ جلب جميع وسائط المنتج (مفصلة)
GET_ALL_PRODUCT_MEDIA_QUERY = """
query GetAllProductMedia($qid: String!) {
    findProductByQid(qid: $qid) {
        id
        qid
        title
        media {
            _id
            fileUrl
            file
            path
            title
            description
            type
            mimetype
            sizeInKB
            sizeInMB
            compressedSizeInKB
            compressedSizeInMB
            width
            height
            alt
            sortOrder
            isFeatured
            createdAt
            updatedAt
        }
    }
}
"""


# ============================================================
# ✏️ MUTATIONS - تحويرات الوسائط
# ============================================================

# 4️⃣ رفع ملف (صورة/فيديو)
UPLOAD_FILE_MUTATION = """
mutation UploadFile($file: String!, $filename: String!, $title: String, $description: String) {
    uploadFile(file: $file, filename: $filename, title: $title, description: $description) {
        success
        message
        data {
            _id
            fileUrl
            file
            path
            mimetype
            sizeInKB
            sizeInMB
            title
            description
            createdAt
        }
    }
}
"""

# 5️⃣ رفع ملفات متعددة
UPLOAD_MULTIPLE_FILES_MUTATION = """
mutation UploadMultipleFiles($files: [FileInput!]!) {
    uploadMultipleFiles(files: $files) {
        success
        message
        data {
            _id
            fileUrl
            file
            path
            mimetype
            sizeInKB
            sizeInMB
            title
            description
            createdAt
        }
    }
}
"""

# 6️⃣ حذف ملف
DELETE_FILE_MUTATION = """
mutation DeleteFile($fileId: String!) {
    deleteFile(fileId: $fileId) {
        success
        message
    }
}
"""

# 7️⃣ تحديث معلومات الملف
UPDATE_FILE_INFO_MUTATION = """
mutation UpdateFileInfo($fileId: String!, $title: String, $description: String, $alt: String) {
    updateFileInfo(fileId: $fileId, title: $title, description: $description, alt: $alt) {
        success
        message
        data {
            _id
            fileUrl
            title
            description
            alt
            updatedAt
        }
    }
}
"""

# 8️⃣ إضافة صورة للمنتج
ADD_PRODUCT_IMAGE_MUTATION = """
mutation AddProductImage($qid: String!, $imageUrl: String!) {
    addProductImage(qid: $qid, imageUrl: $imageUrl) {
        id
        qid
        images {
            _id
            fileUrl
        }
        updatedAt
    }
}
"""

# 9️⃣ إزالة صورة من المنتج
REMOVE_PRODUCT_IMAGE_MUTATION = """
mutation RemoveProductImage($qid: String!, $imageId: String!) {
    removeProductImage(qid: $qid, imageId: $imageId) {
        id
        qid
        images {
            _id
            fileUrl
        }
        updatedAt
    }
}
"""

# 🔟 إضافة وسائط للمنتج
ADD_PRODUCT_MEDIA_MUTATION = """
mutation AddProductMedia($qid: String!, $mediaUrls: [String!]!) {
    addProductMedia(qid: $qid, mediaUrls: $mediaUrls) {
        id
        qid
        media {
            _id
            fileUrl
        }
        updatedAt
    }
}
"""

# 1️⃣1️⃣ إزالة وسائط من المنتج
REMOVE_PRODUCT_MEDIA_MUTATION = """
mutation RemoveProductMedia($qid: String!, $mediaIds: [String!]!) {
    removeProductMedia(qid: $qid, mediaIds: $mediaIds) {
        id
        qid
        media {
            _id
            fileUrl
        }
        updatedAt
    }
}
"""

# 1️⃣2️⃣ تحديث ترتيب صور المنتج
REORDER_PRODUCT_IMAGES_MUTATION = """
mutation ReorderProductImages($qid: String!, $imageIds: [String!]!) {
    reorderProductImages(qid: $qid, imageIds: $imageIds) {
        id
        qid
        images {
            _id
            fileUrl
            sortOrder
        }
        updatedAt
    }
}
"""


# ============================================================
# 🚀 SERVICE CLASS - خدمة الوسائط
# ============================================================

class ProductMediaService:
    """
    خدمة إدارة وسائط المنتجات
    تحتوي على جميع عمليات رفع، حذف، وتحديث الصور والملفات
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 📤 FILE UPLOAD - رفع الملفات
    # ============================================================
    
    def upload_file(self, file_data: bytes, filename: str,
                   title: str = None, description: str = None,
                   file_type: str = None) -> Optional[Dict]:
        """
        رفع ملف (صورة/فيديو/مستند)
        
        Args:
            file_data: بيانات الملف (bytes)
            filename: اسم الملف
            title: عنوان الملف (اختياري)
            description: وصف الملف (اختياري)
            file_type: نوع الملف (image, video, document)
        
        Returns:
            Dict: بيانات الملف المرفوع
        """
        try:
            # تحديد نوع الملف
            if not file_type:
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                    file_type = 'image'
                elif ext in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']:
                    file_type = 'video'
                else:
                    file_type = 'document'
            
            # تحويل الملف إلى base64
            file_base64 = base64.b64encode(file_data).decode('utf-8')
            
            # إعداد الملف للرفع
            if file_type == 'image':
                file_string = f"data:image/{ext};base64,{file_base64}" if ext else f"data:image/jpeg;base64,{file_base64}"
            else:
                file_string = file_base64
            
            variables = {
                "file": file_string,
                "filename": filename
            }
            if title:
                variables["title"] = title
            if description:
                variables["description"] = description
            
            print(f"🔄 جاري رفع الملف: {filename}")
            result = self.client.execute_query(UPLOAD_FILE_MUTATION, variables)
            
            if result:
                upload_result = result.get('uploadFile', {})
                if upload_result.get('success'):
                    data = upload_result.get('data', {})
                    print(f"✅ تم رفع الملف بنجاح: {data.get('fileUrl')}")
                    return data
                else:
                    print(f"❌ فشل رفع الملف: {upload_result.get('message')}")
                    return None
            return None
            
        except Exception as e:
            print(f"❌ خطأ في upload_file: {e}")
            return None
    
    def upload_multiple_files(self, files: List[Dict]) -> List[Dict]:
        """
        رفع ملفات متعددة
        
        Args:
            files: قائمة بالملفات [{file_data: bytes, filename: str, title: str}]
        
        Returns:
            List[Dict]: قائمة بيانات الملفات المرفوعة
        """
        uploaded_files = []
        for file_data in files:
            result = self.upload_file(
                file_data['file_data'],
                file_data['filename'],
                file_data.get('title'),
                file_data.get('description')
            )
            if result:
                uploaded_files.append(result)
        return uploaded_files
    
    # ============================================================
    # 📋 GET MEDIA - جلب الوسائط
    # ============================================================
    
    def get_product_media(self, product_qid: str) -> Dict:
        """
        جلب جميع وسائط المنتج
        
        Args:
            product_qid: معرف المنتج
        
        Returns:
            Dict: {images: List, media: List}
        """
        result = self.client.execute_query(GET_PRODUCT_MEDIA_QUERY, {"qid": product_qid})
        if result:
            product = result.get('findProductByQid', {})
            return {
                'images': product.get('images', []),
                'media': product.get('media', [])
            }
        return {'images': [], 'media': []}
    
    def get_variant_media(self, variant_qid: str) -> Dict:
        """
        جلب وسائط الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
        
        Returns:
            Dict: {images: List, media: List}
        """
        result = self.client.execute_query(GET_VARIANT_MEDIA_QUERY, {"variantQid": variant_qid})
        if result:
            variant = result.get('findVariantById', {})
            return {
                'images': variant.get('images', []),
                'media': variant.get('media', [])
            }
        return {'images': [], 'media': []}
    
    def get_all_product_media(self, product_qid: str) -> List[Dict]:
        """
        جلب جميع وسائط المنتج (مفصلة)
        
        Args:
            product_qid: معرف المنتج
        
        Returns:
            List[Dict]: قائمة مفصلة بالوسائط
        """
        result = self.client.execute_query(GET_ALL_PRODUCT_MEDIA_QUERY, {"qid": product_qid})
        if result:
            product = result.get('findProductByQid', {})
            return product.get('media', [])
        return []
    
    # ============================================================
    # 🗑️ DELETE MEDIA - حذف الوسائط
    # ============================================================
    
    def delete_file(self, file_id: str) -> bool:
        """
        حذف ملف
        
        Args:
            file_id: معرف الملف
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        result = self.client.execute_query(DELETE_FILE_MUTATION, {"fileId": file_id})
        if result:
            delete_result = result.get('deleteFile', {})
            return delete_result.get('success', False)
        return False
    
    def update_file_info(self, file_id: str, title: str = None,
                        description: str = None, alt: str = None) -> Optional[Dict]:
        """
        تحديث معلومات الملف
        
        Args:
            file_id: معرف الملف
            title: العنوان الجديد
            description: الوصف الجديد
            alt: النص البديل للصورة
        
        Returns:
            Dict: بيانات الملف المحدثة
        """
        variables = {"fileId": file_id}
        if title is not None:
            variables["title"] = title
        if description is not None:
            variables["description"] = description
        if alt is not None:
            variables["alt"] = alt
        
        result = self.client.execute_query(UPDATE_FILE_INFO_MUTATION, variables)
        if result:
            update_result = result.get('updateFileInfo', {})
            return update_result.get('data') if update_result.get('success') else None
        return None
    
    # ============================================================
    # 🖼️ PRODUCT IMAGES - صور المنتج
    # ============================================================
    
    def add_product_image(self, product_qid: str, image_url: str) -> Optional[Dict]:
        """
        إضافة صورة للمنتج
        
        Args:
            product_qid: معرف المنتج
            image_url: رابط الصورة
        
        Returns:
            Dict: بيانات المنتج المحدثة
        """
        result = self.client.execute_query(
            ADD_PRODUCT_IMAGE_MUTATION,
            {"qid": product_qid, "imageUrl": image_url}
        )
        return result.get('addProductImage') if result else None
    
    def remove_product_image(self, product_qid: str, image_id: str) -> Optional[Dict]:
        """
        إزالة صورة من المنتج
        
        Args:
            product_qid: معرف المنتج
            image_id: معرف الصورة
        
        Returns:
            Dict: بيانات المنتج المحدثة
        """
        result = self.client.execute_query(
            REMOVE_PRODUCT_IMAGE_MUTATION,
            {"qid": product_qid, "imageId": image_id}
        )
        return result.get('removeProductImage') if result else None
    
    def add_product_media(self, product_qid: str, media_urls: List[str]) -> Optional[Dict]:
        """
        إضافة وسائط للمنتج
        
        Args:
            product_qid: معرف المنتج
            media_urls: قائمة روابط الوسائط
        
        Returns:
            Dict: بيانات المنتج المحدثة
        """
        result = self.client.execute_query(
            ADD_PRODUCT_MEDIA_MUTATION,
            {"qid": product_qid, "mediaUrls": media_urls}
        )
        return result.get('addProductMedia') if result else None
    
    def remove_product_media(self, product_qid: str, media_ids: List[str]) -> Optional[Dict]:
        """
        إزالة وسائط من المنتج
        
        Args:
            product_qid: معرف المنتج
            media_ids: قائمة معرفات الوسائط
        
        Returns:
            Dict: بيانات المنتج المحدثة
        """
        result = self.client.execute_query(
            REMOVE_PRODUCT_MEDIA_MUTATION,
            {"qid": product_qid, "mediaIds": media_ids}
        )
        return result.get('removeProductMedia') if result else None
    
    def reorder_product_images(self, product_qid: str, image_ids: List[str]) -> Optional[Dict]:
        """
        تحديث ترتيب صور المنتج
        
        Args:
            product_qid: معرف المنتج
            image_ids: قائمة معرفات الصور بالترتيب الجديد
        
        Returns:
            Dict: بيانات المنتج المحدثة
        """
        result = self.client.execute_query(
            REORDER_PRODUCT_IMAGES_MUTATION,
            {"qid": product_qid, "imageIds": image_ids}
        )
        return result.get('reorderProductImages') if result else None
    
    # ============================================================
    # 🔄 BULK OPERATIONS - عمليات دفعة واحدة
    # ============================================================
    
    def upload_and_add_images(self, product_qid: str,
                             image_files: List[Dict]) -> List[str]:
        """
        رفع صور وإضافتها للمنتج
        
        Args:
            product_qid: معرف المنتج
            image_files: قائمة ملفات الصور [{file_data: bytes, filename: str}]
        
        Returns:
            List[str]: قائمة روابط الصور المرفوعة
        """
        uploaded_urls = []
        
        for image_file in image_files:
            # رفع الصورة
            file_data = self.upload_file(
                image_file['file_data'],
                image_file['filename'],
                title=image_file.get('title'),
                description=image_file.get('description')
            )
            
            if file_data and file_data.get('fileUrl'):
                # إضافة الصورة للمنتج
                self.add_product_image(product_qid, file_data['fileUrl'])
                uploaded_urls.append(file_data['fileUrl'])
        
        return uploaded_urls
    
    def get_product_images_urls(self, product_qid: str) -> List[str]:
        """
        جلب روابط صور المنتج فقط
        
        Args:
            product_qid: معرف المنتج
        
        Returns:
            List[str]: قائمة روابط الصور
        """
        media = self.get_product_media(product_qid)
        return [img.get('fileUrl') for img in media.get('images', []) if img.get('fileUrl')]
    
    def get_media_stats(self, product_qid: str) -> Dict:
        """
        الحصول على إحصائيات وسائط المنتج
        
        Args:
            product_qid: معرف المنتج
        
        Returns:
            Dict: {totalImages, totalMedia, totalSize, averageSize}
        """
        media = self.get_product_media(product_qid)
        images = media.get('images', [])
        all_media = media.get('media', [])
        
        total_size = 0
        for img in images:
            total_size += img.get('sizeInKB', 0)
        for m in all_media:
            total_size += m.get('sizeInKB', 0)
        
        total_items = len(images) + len(all_media)
        
        return {
            'totalImages': len(images),
            'totalMedia': len(all_media),
            'totalItems': total_items,
            'totalSizeKB': total_size,
            'totalSizeMB': total_size / 1024 if total_size > 0 else 0,
            'averageSizeKB': total_size / total_items if total_items > 0 else 0
        }


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_media = ProductMediaService()


# ============================================================
# 📋 EXPORTS - للاستخدام المباشر
# ============================================================

__all__ = [
    'GET_PRODUCT_MEDIA_QUERY',
    'GET_VARIANT_MEDIA_QUERY',
    'GET_ALL_PRODUCT_MEDIA_QUERY',
    'UPLOAD_FILE_MUTATION',
    'UPLOAD_MULTIPLE_FILES_MUTATION',
    'DELETE_FILE_MUTATION',
    'UPDATE_FILE_INFO_MUTATION',
    'ADD_PRODUCT_IMAGE_MUTATION',
    'REMOVE_PRODUCT_IMAGE_MUTATION',
    'ADD_PRODUCT_MEDIA_MUTATION',
    'REMOVE_PRODUCT_MEDIA_MUTATION',
    'REORDER_PRODUCT_IMAGES_MUTATION',
    'ProductMediaService',
    'product_media'
]


# ============================================================
# 🧪 TEST - اختبار سريع (اختياري)
# ============================================================

if __name__ == "__main__":
    service = ProductMediaService()
    
    # جلب وسائط منتج
    # media = service.get_product_media("product_qid_here")
    # print(f"✅ الصور: {len(media.get('images', []))}")
    
    print("✅ Product Media Extras Service ready!")
