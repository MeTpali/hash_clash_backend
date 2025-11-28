from typing import Optional, List
import logging
from fastapi import HTTPException, status

from repositories.text import TextRepository
from core.schemas.text import (
    TextCreateRequest, TextCreateResponse,
    TextUpdateRequest, TextUpdateResponse,
    TextDeleteRequest, TextDeleteResponse,
    TextGetRequest, TextGetResponse,
    TextListRequest, TextListResponse
)
from core.models.text import Text
from core.utils.rsa import rsa_encrypt, rsa_decrypt
from core.utils.kuznechik import grasshopper_encrypt, grasshopper_decrypt

logger = logging.getLogger(__name__)


class TextService:
    def __init__(self, repository: TextRepository):
        self.repository = repository

    async def create_text(self, text_data: TextCreateRequest) -> TextCreateResponse:
        """
        Создание нового текста.
        
        Args:
            text_data: Данные для создания текста
            
        Returns:
            TextCreateResponse: Результат создания текста
            
        Raises:
            HTTPException: Если произошла ошибка при создании
        """
        logger.info(f"Creating new text for user_id: {text_data.user_id}")
        
        # Валидация типа шифрования
        if text_data.encryption_type not in ["rsa", "grasshopper"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип шифрования должен быть 'rsa' или 'grasshopper'"
            )
        
        # Валидация текста
        if not text_data.text or len(text_data.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Текст не может быть пустым"
            )
        
        if len(text_data.text) > 10000:  # Ограничение на размер текста
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Текст слишком длинный (максимум 10000 символов)"
            )
        
        # Шифрование текста перед сохранением
        text_to_save = text_data.text
        if text_data.encryption_type == "rsa":
            try:
                text_to_save = rsa_encrypt(text_data.text)
                logger.info(f"Text encrypted with RSA for user_id: {text_data.user_id}")
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при шифровании RSA: {str(e)}"
                )
        # Шифрование для grasshopper (Kuznechik)
        elif text_data.encryption_type == "grasshopper":
            try:
                text_to_save = grasshopper_encrypt(text_data.text)
                logger.info(f"Text encrypted with Grasshopper (Kuznechik) for user_id: {text_data.user_id}")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при шифровании Grasshopper: {str(e)}"
                )
        
        # Создаем копию данных с зашифрованным текстом
        text_data_copy = TextCreateRequest(
            user_id=text_data.user_id,
            encryption_type=text_data.encryption_type,
            text=text_to_save
        )
        
        text = await self.repository.create_text(text_data_copy)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании текста"
            )
        
        response = TextCreateResponse(
            id=text.id,
            user_id=text.user_id,
            encryption_type=text.encryption_type,
            created_at=text.created_at,
            message="Текст успешно создан"
        )
        
        logger.info(f"Successfully created text with id: {text.id}")
        return response

    async def get_text(self, text_id: int, user_id: int) -> TextGetResponse:
        """
        Получение текста по ID.
        
        Args:
            text_id: ID текста
            user_id: ID пользователя (для авторизации)
            
        Returns:
            TextGetResponse: Данные текста
            
        Raises:
            HTTPException: Если текст не найден или не принадлежит пользователю
        """
        logger.info(f"Getting text id: {text_id} for user_id: {user_id}")
        
        text = await self.repository.get_text_by_id_and_user(text_id, user_id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текст с id {text_id} не найден или не принадлежит вам"
            )
        
        # Расшифровка текста при получении
        decrypted_text = text.text
        if text.encryption_type == "rsa":
            try:
                decrypted_text = rsa_decrypt(text.text)
                logger.info(f"Text decrypted with RSA for text_id: {text_id}")
            except Exception as e:
                logger.error(f"Error decrypting RSA text id {text_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при расшифровке текста: {str(e)}"
                )
        # Расшифровка для grasshopper
        elif text.encryption_type == "grasshopper":
            try:
                decrypted_text = grasshopper_decrypt(text.text)
                logger.info(f"Text decrypted with Grasshopper (Kuznechik) for text_id: {text_id}")
            except Exception as e:
                logger.error(f"Error decrypting Grasshopper text id {text_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при расшифровке текста: {str(e)}"
                )
        
        response = TextGetResponse(
            id=text.id,
            user_id=text.user_id,
            encryption_type=text.encryption_type,
            text=decrypted_text,
            is_active=text.is_active,
            created_at=text.created_at
        )
        
        logger.info(f"Successfully retrieved text id: {text_id}")
        return response

    async def update_text(self, text_id: int, user_id: int, update_data: TextUpdateRequest) -> TextUpdateResponse:
        """
        Обновление текста.
        
        Args:
            text_id: ID текста
            user_id: ID пользователя (для авторизации)
            update_data: Данные для обновления
            
        Returns:
            TextUpdateResponse: Результат обновления
            
        Raises:
            HTTPException: Если текст не найден или произошла ошибка
        """
        logger.info(f"Updating text id: {text_id} for user_id: {user_id}")
        
        # Валидация типа шифрования, если указан
        if update_data.encryption_type and update_data.encryption_type not in ["rsa", "grasshopper"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип шифрования должен быть 'rsa' или 'grasshopper'"
            )
        
        # Валидация текста, если указан
        if update_data.text is not None:
            if not update_data.text or len(update_data.text.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Текст не может быть пустым"
                )
            
            if len(update_data.text) > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Текст слишком длинный (максимум 10000 символов)"
                )
        
        # Проверяем, что есть что обновлять
        if all(field is None for field in [update_data.encryption_type, update_data.text, update_data.is_active]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Необходимо указать хотя бы одно поле для обновления"
            )
        
        # Получаем текущий текст для определения типа шифрования
        current_text = await self.repository.get_text_by_id_and_user(text_id, user_id)
        if not current_text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текст с id {text_id} не найден или не принадлежит вам"
            )
        
        # Определяем тип шифрования для использования
        encryption_type_to_use = update_data.encryption_type if update_data.encryption_type is not None else current_text.encryption_type
        
        # Шифрование текста перед обновлением, если текст указан
        if update_data.text is not None:
            text_to_save = update_data.text
            if encryption_type_to_use == "rsa":
                try:
                    text_to_save = rsa_encrypt(update_data.text)
                    logger.info(f"Text encrypted with RSA for update text_id: {text_id}")
                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ошибка при шифровании RSA: {str(e)}"
                    )
            # Шифрование для grasshopper (Kuznechik)
            elif encryption_type_to_use == "grasshopper":
                try:
                    text_to_save = grasshopper_encrypt(update_data.text)
                    logger.info(f"Text encrypted with Grasshopper (Kuznechik) for update text_id: {text_id}")
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ошибка при шифровании Grasshopper: {str(e)}"
                    )
            
            # Обновляем текст в данных обновления
            update_data.text = text_to_save
        
        # Если изменяется тип шифрования, нужно перешифровать существующий текст
        if update_data.encryption_type is not None and update_data.encryption_type != current_text.encryption_type:
            # Получаем расшифрованный текст
            plain_text = current_text.text
            if current_text.encryption_type == "rsa":
                try:
                    plain_text = rsa_decrypt(current_text.text)
                    logger.info(f"Text decrypted from RSA for re-encryption text_id: {text_id}")
                except Exception as e:
                    logger.error(f"Error decrypting RSA text id {text_id} for re-encryption: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Ошибка при расшифровке текста для перешифрования: {str(e)}"
                    )
            # Если был grasshopper, расшифровываем
            elif current_text.encryption_type == "grasshopper":
                try:
                    plain_text = grasshopper_decrypt(current_text.text)
                    logger.info(f"Text decrypted from Grasshopper for re-encryption text_id: {text_id}")
                except Exception as e:
                    logger.error(f"Error decrypting Grasshopper text id {text_id} for re-encryption: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Ошибка при расшифровке текста для перешифрования: {str(e)}"
                    )
            
            # Шифруем в новый тип, если текст не был указан в update_data
            if update_data.text is None:
                if update_data.encryption_type == "rsa":
                    try:
                        update_data.text = rsa_encrypt(plain_text)
                        logger.info(f"Text re-encrypted to RSA for text_id: {text_id}")
                    except ValueError as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ошибка при перешифровании в RSA: {str(e)}"
                        )
                elif update_data.encryption_type == "grasshopper":
                    try:
                        update_data.text = grasshopper_encrypt(plain_text)
                        logger.info(f"Text re-encrypted to Grasshopper for text_id: {text_id}")
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ошибка при перешифровании в Grasshopper: {str(e)}"
                        )
        
        text = await self.repository.update_text(text_id, user_id, update_data)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текст с id {text_id} не найден или не принадлежит вам"
            )
        
        # Расшифровка текста при возврате
        decrypted_text = text.text
        if text.encryption_type == "rsa":
            try:
                decrypted_text = rsa_decrypt(text.text)
                logger.info(f"Text decrypted with RSA for update response text_id: {text_id}")
            except Exception as e:
                logger.error(f"Error decrypting RSA text id {text_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при расшифровке текста: {str(e)}"
                )
        # Расшифровка для grasshopper
        elif text.encryption_type == "grasshopper":
            try:
                decrypted_text = grasshopper_decrypt(text.text)
                logger.info(f"Text decrypted with Grasshopper (Kuznechik) for update response text_id: {text_id}")
            except Exception as e:
                logger.error(f"Error decrypting Grasshopper text id {text_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при расшифровке текста: {str(e)}"
                )
        
        response = TextUpdateResponse(
            id=text.id,
            user_id=text.user_id,
            encryption_type=text.encryption_type,
            text=decrypted_text,
            is_active=text.is_active,
            created_at=text.created_at,
            message="Текст успешно обновлен"
        )
        
        logger.info(f"Successfully updated text id: {text_id}")
        return response

    async def delete_text(self, text_id: int, user_id: int) -> TextDeleteResponse:
        """
        Удаление текста (мягкое удаление).
        
        Args:
            text_id: ID текста
            user_id: ID пользователя (для авторизации)
            
        Returns:
            TextDeleteResponse: Результат удаления
            
        Raises:
            HTTPException: Если текст не найден
        """
        logger.info(f"Deleting text id: {text_id} for user_id: {user_id}")
        
        success = await self.repository.delete_text(text_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текст с id {text_id} не найден или не принадлежит вам"
            )
        
        response = TextDeleteResponse(
            id=text_id,
            message="Текст успешно удален"
        )
        
        logger.info(f"Successfully deleted text id: {text_id}")
        return response

    async def get_user_texts(self, user_id: int, is_active: Optional[bool] = None, 
                           encryption_type: Optional[str] = None) -> TextListResponse:
        """
        Получение списка текстов пользователя.
        
        Args:
            user_id: ID пользователя
            is_active: Фильтр по активности (опционально)
            encryption_type: Фильтр по типу шифрования (опционально)
            
        Returns:
            TextListResponse: Список текстов пользователя
            
        Raises:
            HTTPException: Если указан неверный тип шифрования
        """
        logger.info(f"Getting texts for user_id: {user_id}")
        
        # Валидация типа шифрования, если указан
        if encryption_type and encryption_type not in ["rsa", "grasshopper"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тип шифрования должен быть 'rsa' или 'grasshopper'"
            )
        
        texts = await self.repository.get_user_texts(user_id, is_active, encryption_type)
        
        # Преобразуем модели в схемы ответа с расшифровкой
        text_responses = []
        for text in texts:
            # Расшифровка текста при получении
            decrypted_text = text.text
            if text.encryption_type == "rsa":
                try:
                    decrypted_text = rsa_decrypt(text.text)
                except Exception as e:
                    logger.error(f"Error decrypting RSA text id {text.id}: {str(e)}")
                    # Пропускаем текст, который не удалось расшифровать
                    continue
            elif text.encryption_type == "grasshopper":
                try:
                    decrypted_text = grasshopper_decrypt(text.text)
                except Exception as e:
                    logger.error(f"Error decrypting Grasshopper text id {text.id}: {str(e)}")
                    # Пропускаем текст, который не удалось расшифровать
                    continue
            
            text_responses.append(
                TextGetResponse(
                    id=text.id,
                    user_id=text.user_id,
                    encryption_type=text.encryption_type,
                    text=decrypted_text,
                    is_active=text.is_active,
                    created_at=text.created_at
                )
            )
        
        response = TextListResponse(
            texts=text_responses,
            total_count=len(text_responses),
            message=f"Найдено {len(text_responses)} текстов"
        )
        
        logger.info(f"Successfully retrieved {len(text_responses)} texts for user_id: {user_id}")
        return response

    async def get_text_by_id_admin(self, text_id: int) -> TextGetResponse:
        """
        Получение текста по ID для администратора (без проверки владельца).
        
        Args:
            text_id: ID текста
            
        Returns:
            TextGetResponse: Данные текста
            
        Raises:
            HTTPException: Если текст не найден
        """
        logger.info(f"Getting text id: {text_id} (admin access)")
        
        text = await self.repository.get_text_by_id(text_id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Текст с id {text_id} не найден"
            )
        
        # Расшифровка текста при получении
        decrypted_text = text.text
        if text.encryption_type == "rsa":
            try:
                decrypted_text = rsa_decrypt(text.text)
                logger.info(f"Text decrypted with RSA for admin access text_id: {text_id}")
            except Exception as e:
                logger.error(f"Error decrypting RSA text id {text_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при расшифровке текста: {str(e)}"
                )
        # Расшифровка для grasshopper
        elif text.encryption_type == "grasshopper":
            try:
                decrypted_text = grasshopper_decrypt(text.text)
                logger.info(f"Text decrypted with Grasshopper (Kuznechik) for admin access text_id: {text_id}")
            except Exception as e:
                logger.error(f"Error decrypting Grasshopper text id {text_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при расшифровке текста: {str(e)}"
                )
        
        response = TextGetResponse(
            id=text.id,
            user_id=text.user_id,
            encryption_type=text.encryption_type,
            text=decrypted_text,
            is_active=text.is_active,
            created_at=text.created_at
        )
        
        logger.info(f"Successfully retrieved text id: {text_id} (admin access)")
        return response

    async def get_all_texts_admin(self) -> TextListResponse:
        """
        Получение всех текстов для администратора.
        
        Returns:
            TextListResponse: Список всех текстов
        """
        logger.info("Getting all texts (admin access)")
        
        texts = await self.repository.get_all_texts()
        
        # Преобразуем модели в схемы ответа с расшифровкой
        text_responses = []
        for text in texts:
            # Расшифровка текста при получении
            decrypted_text = text.text
            if text.encryption_type == "rsa":
                try:
                    decrypted_text = rsa_decrypt(text.text)
                except Exception as e:
                    logger.error(f"Error decrypting RSA text id {text.id}: {str(e)}")
                    # Пропускаем текст, который не удалось расшифровать
                    continue
            elif text.encryption_type == "grasshopper":
                try:
                    decrypted_text = grasshopper_decrypt(text.text)
                except Exception as e:
                    logger.error(f"Error decrypting Grasshopper text id {text.id}: {str(e)}")
                    # Пропускаем текст, который не удалось расшифровать
                    continue
            
            text_responses.append(
                TextGetResponse(
                    id=text.id,
                    user_id=text.user_id,
                    encryption_type=text.encryption_type,
                    text=decrypted_text,
                    is_active=text.is_active,
                    created_at=text.created_at
                )
            )
        
        response = TextListResponse(
            texts=text_responses,
            total_count=len(text_responses),
            message=f"Найдено {len(text_responses)} текстов (всего)"
        )
        
        logger.info(f"Successfully retrieved {len(text_responses)} texts (admin access)")
        return response