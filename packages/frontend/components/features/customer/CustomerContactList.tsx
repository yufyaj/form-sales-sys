'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion, AnimatePresence } from 'framer-motion'
import {
  createClientContactSchema,
  updateClientContactSchema,
  type CreateClientContactFormData,
  type UpdateClientContactFormData,
} from '@/lib/validations/customer'
import type { ClientContact } from '@/types/customer'
import { staggerContainer, staggerItem } from '@/lib/motion'
import { sanitizeEmail } from '@/lib/utils'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Badge from '@/components/ui/Badge'
import Card from '@/components/ui/Card'

interface CustomerContactListProps {
  clientOrganizationId: number
  contacts: ClientContact[]
  onAddContact: (data: CreateClientContactFormData) => Promise<void>
  onUpdateContact: (
    contactId: number,
    data: UpdateClientContactFormData
  ) => Promise<void>
  onDeleteContact: (contactId: number) => Promise<void>
  isLoading?: boolean
}

/**
 * 顧客担当者管理コンポーネント
 *
 * 担当者の追加、編集、削除機能を提供
 */
export default function CustomerContactList({
  clientOrganizationId,
  contacts,
  onAddContact,
  onUpdateContact,
  onDeleteContact,
  isLoading = false,
}: CustomerContactListProps) {
  const [isAddingContact, setIsAddingContact] = useState(false)
  const [editingContactId, setEditingContactId] = useState<number | null>(null)
  const [serverError, setServerError] = useState<string>('')

  // 新規追加フォーム
  const addForm = useForm<CreateClientContactFormData>({
    resolver: zodResolver(createClientContactSchema),
    mode: 'onBlur',
    defaultValues: {
      clientOrganizationId,
      fullName: '',
      department: '',
      position: '',
      email: '',
      phone: '',
      mobile: '',
      isPrimary: false,
      notes: '',
    },
  })

  // 編集フォーム
  const editForm = useForm<UpdateClientContactFormData>({
    resolver: zodResolver(updateClientContactSchema),
    mode: 'onBlur',
  })

  const handleAddSubmit = async (data: CreateClientContactFormData) => {
    setServerError('')
    try {
      await onAddContact({ ...data, clientOrganizationId })
      addForm.reset()
      setIsAddingContact(false)
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : 'エラーが発生しました'
      )
    }
  }

  const handleEditSubmit = async (data: UpdateClientContactFormData) => {
    if (editingContactId === null) return
    setServerError('')
    try {
      await onUpdateContact(editingContactId, data)
      editForm.reset()
      setEditingContactId(null)
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : 'エラーが発生しました'
      )
    }
  }

  const handleEditStart = (contact: ClientContact) => {
    setEditingContactId(contact.id)
    editForm.reset({
      fullName: contact.fullName,
      department: contact.department || '',
      position: contact.position || '',
      email: contact.email || '',
      phone: contact.phone || '',
      mobile: contact.mobile || '',
      isPrimary: contact.isPrimary,
      notes: contact.notes || '',
    })
  }

  const handleDelete = async (contactId: number) => {
    if (!confirm('この担当者を削除してもよろしいですか？')) return
    setServerError('')
    try {
      await onDeleteContact(contactId)
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : 'エラーが発生しました'
      )
    }
  }

  const MotionForm = motion.form
  const MotionDiv = motion.div

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">担当者一覧</h3>
        {!isAddingContact && (
          <Button
            onClick={() => setIsAddingContact(true)}
            variant="outline"
            size="sm"
          >
            担当者を追加
          </Button>
        )}
      </div>

      {/* エラー表示 */}
      {serverError && (
        <div
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
        >
          {serverError}
        </div>
      )}

      {/* 担当者追加フォーム */}
      <AnimatePresence>
        {isAddingContact && (
          <MotionDiv
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card>
              <MotionForm
                onSubmit={addForm.handleSubmit(handleAddSubmit)}
                className="space-y-4"
                noValidate
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
              >
                <h4 className="font-medium text-gray-900">新しい担当者を追加</h4>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <Input
                    label="氏名 *"
                    type="text"
                    placeholder="山田 太郎"
                    error={addForm.formState.errors.fullName?.message}
                    {...addForm.register('fullName')}
                  />
                  <Input
                    label="部署"
                    type="text"
                    placeholder="営業部"
                    error={addForm.formState.errors.department?.message}
                    {...addForm.register('department')}
                  />
                  <Input
                    label="役職"
                    type="text"
                    placeholder="部長"
                    error={addForm.formState.errors.position?.message}
                    {...addForm.register('position')}
                  />
                  <Input
                    label="メールアドレス"
                    type="email"
                    placeholder="yamada@example.com"
                    error={addForm.formState.errors.email?.message}
                    {...addForm.register('email')}
                  />
                  <Input
                    label="電話番号"
                    type="tel"
                    placeholder="03-1234-5678"
                    error={addForm.formState.errors.phone?.message}
                    {...addForm.register('phone')}
                  />
                  <Input
                    label="携帯電話番号"
                    type="tel"
                    placeholder="090-1234-5678"
                    error={addForm.formState.errors.mobile?.message}
                    {...addForm.register('mobile')}
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="isPrimary-add"
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    {...addForm.register('isPrimary')}
                  />
                  <label
                    htmlFor="isPrimary-add"
                    className="ml-2 text-sm text-gray-700"
                  >
                    主担当者として設定
                  </label>
                </div>

                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsAddingContact(false)
                      addForm.reset()
                    }}
                    disabled={isLoading}
                  >
                    キャンセル
                  </Button>
                  <Button
                    type="submit"
                    size="sm"
                    isLoading={isLoading}
                    disabled={isLoading}
                  >
                    追加
                  </Button>
                </div>
              </MotionForm>
            </Card>
          </MotionDiv>
        )}
      </AnimatePresence>

      {/* 担当者リスト */}
      {contacts.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-500">担当者が登録されていません</p>
        </div>
      ) : (
        <div className="space-y-3">
          {contacts.map((contact) => (
            <Card key={contact.id}>
              {editingContactId === contact.id ? (
                <MotionForm
                  onSubmit={editForm.handleSubmit(handleEditSubmit)}
                  className="space-y-4"
                  noValidate
                  variants={staggerContainer}
                  initial="hidden"
                  animate="visible"
                >
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <Input
                      label="氏名 *"
                      type="text"
                      error={editForm.formState.errors.fullName?.message}
                      {...editForm.register('fullName')}
                    />
                    <Input
                      label="部署"
                      type="text"
                      error={editForm.formState.errors.department?.message}
                      {...editForm.register('department')}
                    />
                    <Input
                      label="役職"
                      type="text"
                      error={editForm.formState.errors.position?.message}
                      {...editForm.register('position')}
                    />
                    <Input
                      label="メールアドレス"
                      type="email"
                      error={editForm.formState.errors.email?.message}
                      {...editForm.register('email')}
                    />
                    <Input
                      label="電話番号"
                      type="tel"
                      error={editForm.formState.errors.phone?.message}
                      {...editForm.register('phone')}
                    />
                    <Input
                      label="携帯電話番号"
                      type="tel"
                      error={editForm.formState.errors.mobile?.message}
                      {...editForm.register('mobile')}
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id={`isPrimary-${contact.id}`}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      {...editForm.register('isPrimary')}
                    />
                    <label
                      htmlFor={`isPrimary-${contact.id}`}
                      className="ml-2 text-sm text-gray-700"
                    >
                      主担当者として設定
                    </label>
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingContactId(null)
                        editForm.reset()
                      }}
                      disabled={isLoading}
                    >
                      キャンセル
                    </Button>
                    <Button
                      type="submit"
                      size="sm"
                      isLoading={isLoading}
                      disabled={isLoading}
                    >
                      更新
                    </Button>
                  </div>
                </MotionForm>
              ) : (
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-gray-900">
                        {contact.fullName}
                      </h4>
                      {contact.isPrimary && (
                        <Badge variant="info" size="sm">
                          主担当
                        </Badge>
                      )}
                    </div>
                    <div className="mt-2 space-y-1 text-sm text-gray-600">
                      {contact.position && (
                        <p>
                          {contact.department && `${contact.department} / `}
                          {contact.position}
                        </p>
                      )}
                      {contact.email && (
                        <p>
                          <a
                            href={`mailto:${sanitizeEmail(contact.email)}`}
                            className="text-blue-600 hover:underline"
                          >
                            {contact.email}
                          </a>
                        </p>
                      )}
                      {contact.phone && <p>TEL: {contact.phone}</p>}
                      {contact.mobile && <p>携帯: {contact.mobile}</p>}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditStart(contact)}
                      disabled={isLoading}
                    >
                      編集
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(contact.id)}
                      disabled={isLoading}
                    >
                      削除
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
