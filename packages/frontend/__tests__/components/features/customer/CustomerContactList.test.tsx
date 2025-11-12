import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CustomerContactList from '@/components/features/customer/CustomerContactList'
import type { ClientContact } from '@/types/customer'

describe('CustomerContactList', () => {
  const mockContacts: ClientContact[] = [
    {
      id: 1,
      clientOrganizationId: 1,
      fullName: '田中 一郎',
      department: '営業部',
      position: '部長',
      email: 'tanaka@example.com',
      phone: '03-1234-5678',
      mobile: '090-1234-5678',
      isPrimary: true,
      notes: null,
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
      deletedAt: null,
    },
    {
      id: 2,
      clientOrganizationId: 1,
      fullName: '鈴木 花子',
      department: '総務部',
      position: '課長',
      email: 'suzuki@example.com',
      phone: '03-1234-5679',
      mobile: null,
      isPrimary: false,
      notes: null,
      createdAt: '2025-01-02T00:00:00Z',
      updatedAt: '2025-01-02T00:00:00Z',
      deletedAt: null,
    },
  ]

  const mockOnAddContact = jest.fn()
  const mockOnUpdateContact = jest.fn()
  const mockOnDeleteContact = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    // window.confirmをモック
    global.confirm = jest.fn(() => true)
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('担当者一覧表示', () => {
    it('担当者一覧のヘッダーが表示される', () => {
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      expect(screen.getByText('担当者一覧')).toBeInTheDocument()
    })

    it('全ての担当者が表示される', () => {
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      expect(screen.getByText('田中 一郎')).toBeInTheDocument()
      expect(screen.getByText('鈴木 花子')).toBeInTheDocument()
    })

    it('主担当者にはバッジが表示される', () => {
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      expect(screen.getByText('主担当')).toBeInTheDocument()
    })

    it('担当者の詳細情報が表示される', () => {
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      expect(screen.getByText('営業部 / 部長')).toBeInTheDocument()
      expect(screen.getByText('tanaka@example.com')).toBeInTheDocument()
      expect(screen.getByText('TEL: 03-1234-5678')).toBeInTheDocument()
      expect(screen.getByText('携帯: 090-1234-5678')).toBeInTheDocument()
    })

    it('担当者が0件の場合、適切なメッセージが表示される', () => {
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={[]}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      expect(screen.getByText('担当者が登録されていません')).toBeInTheDocument()
    })
  })

  describe('担当者追加', () => {
    it('担当者を追加ボタンが表示される', () => {
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      expect(
        screen.getByRole('button', { name: '担当者を追加' })
      ).toBeInTheDocument()
    })

    it('担当者を追加ボタンをクリックすると、フォームが表示される', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const addButton = screen.getByRole('button', { name: '担当者を追加' })
      await user.click(addButton)

      expect(screen.getByText('新しい担当者を追加')).toBeInTheDocument()
      expect(screen.getByLabelText('氏名 *')).toBeInTheDocument()
    })

    it('担当者追加フォームで全ての項目が入力できる', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const addButton = screen.getByRole('button', { name: '担当者を追加' })
      await user.click(addButton)

      const nameInput = screen.getByLabelText('氏名 *')
      const deptInput = screen.getByLabelText('部署')
      const posInput = screen.getByLabelText('役職')
      const emailInput = screen.getByLabelText('メールアドレス')
      const phoneInput = screen.getByLabelText('電話番号')
      const mobileInput = screen.getByLabelText('携帯電話番号')

      await user.type(nameInput, '山田 太郎')
      await user.type(deptInput, '開発部')
      await user.type(posInput, 'エンジニア')
      await user.type(emailInput, 'yamada@example.com')
      await user.type(phoneInput, '03-9999-9999')
      await user.type(mobileInput, '090-9999-9999')

      expect((nameInput as HTMLInputElement).value).toBe('山田 太郎')
      expect((deptInput as HTMLInputElement).value).toBe('開発部')
      expect((posInput as HTMLInputElement).value).toBe('エンジニア')
      expect((emailInput as HTMLInputElement).value).toBe('yamada@example.com')
      expect((phoneInput as HTMLInputElement).value).toBe('03-9999-9999')
      expect((mobileInput as HTMLInputElement).value).toBe('090-9999-9999')
    })

    it('担当者追加フォームを送信すると、onAddContactが呼ばれる', async () => {
      const user = userEvent.setup()
      mockOnAddContact.mockResolvedValue(undefined)

      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const addButton = screen.getByRole('button', { name: '担当者を追加' })
      await user.click(addButton)

      await user.type(screen.getByLabelText('氏名 *'), '山田 太郎')
      await user.type(screen.getByLabelText('部署'), '開発部')
      await user.type(screen.getByLabelText('メールアドレス'), 'yamada@example.com')

      const submitButton = screen.getByRole('button', { name: '追加' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnAddContact).toHaveBeenCalledTimes(1)
        expect(mockOnAddContact).toHaveBeenCalledWith(
          expect.objectContaining({
            clientOrganizationId: 1,
            fullName: '山田 太郎',
            department: '開発部',
            email: 'yamada@example.com',
          })
        )
      })
    })

    it('キャンセルボタンで追加フォームが閉じる', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const addButton = screen.getByRole('button', { name: '担当者を追加' })
      await user.click(addButton)

      expect(screen.getByText('新しい担当者を追加')).toBeInTheDocument()

      const cancelButtons = screen.getAllByRole('button', { name: 'キャンセル' })
      await user.click(cancelButtons[0])

      await waitFor(() => {
        expect(
          screen.queryByText('新しい担当者を追加')
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('担当者編集', () => {
    it('編集ボタンをクリックすると、編集フォームが表示される', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const editButtons = screen.getAllByRole('button', { name: '編集' })
      await user.click(editButtons[0])

      // 編集フォームの入力フィールドが表示されることを確認
      const nameInputs = screen.getAllByLabelText('氏名 *')
      expect(nameInputs.length).toBeGreaterThan(0)
    })

    it('編集フォームに既存の値が設定される', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const editButtons = screen.getAllByRole('button', { name: '編集' })
      await user.click(editButtons[0])

      const nameInput = screen.getAllByLabelText('氏名 *')[0] as HTMLInputElement
      expect(nameInput.value).toBe('田中 一郎')
    })

    it('編集フォームを送信すると、onUpdateContactが呼ばれる', async () => {
      const user = userEvent.setup()
      mockOnUpdateContact.mockResolvedValue(undefined)

      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const editButtons = screen.getAllByRole('button', { name: '編集' })
      await user.click(editButtons[0])

      const nameInput = screen.getAllByLabelText('氏名 *')[0]
      await user.clear(nameInput)
      await user.type(nameInput, '田中 次郎')

      const updateButton = screen.getByRole('button', { name: '更新' })
      await user.click(updateButton)

      await waitFor(() => {
        expect(mockOnUpdateContact).toHaveBeenCalledTimes(1)
        expect(mockOnUpdateContact).toHaveBeenCalledWith(
          1,
          expect.objectContaining({
            fullName: '田中 次郎',
          })
        )
      })
    })
  })

  describe('担当者削除', () => {
    it('削除ボタンをクリックすると、確認ダイアログが表示される', async () => {
      const user = userEvent.setup()
      const confirmSpy = jest.spyOn(window, 'confirm')

      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: '削除' })
      await user.click(deleteButtons[0])

      expect(confirmSpy).toHaveBeenCalledWith(
        'この担当者を削除してもよろしいですか？'
      )
    })

    it('削除を確認すると、onDeleteContactが呼ばれる', async () => {
      const user = userEvent.setup()
      mockOnDeleteContact.mockResolvedValue(undefined)

      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: '削除' })
      await user.click(deleteButtons[0])

      await waitFor(() => {
        expect(mockOnDeleteContact).toHaveBeenCalledTimes(1)
        expect(mockOnDeleteContact).toHaveBeenCalledWith(1)
      })
    })

    it('削除をキャンセルすると、onDeleteContactが呼ばれない', async () => {
      const user = userEvent.setup()
      global.confirm = jest.fn(() => false)

      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: '削除' })
      await user.click(deleteButtons[0])

      expect(mockOnDeleteContact).not.toHaveBeenCalled()
    })
  })

  describe('バリデーション', () => {
    it('氏名が空の場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const addButton = screen.getByRole('button', { name: '担当者を追加' })
      await user.click(addButton)

      const nameInput = screen.getByLabelText('氏名 *')
      await user.click(nameInput)
      await user.tab()

      await waitFor(() => {
        expect(screen.getByText(/氏名を入力してください/i)).toBeInTheDocument()
      })
    })

    it('無効なメールアドレス形式でエラーが表示される', async () => {
      const user = userEvent.setup()
      render(
        <CustomerContactList
          clientOrganizationId={1}
          contacts={mockContacts}
          onAddContact={mockOnAddContact}
          onUpdateContact={mockOnUpdateContact}
          onDeleteContact={mockOnDeleteContact}
        />
      )

      const addButton = screen.getByRole('button', { name: '担当者を追加' })
      await user.click(addButton)

      const emailInput = screen.getByLabelText('メールアドレス')
      await user.type(emailInput, 'invalid-email')
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText(/有効なメールアドレスを入力してください/i)
        ).toBeInTheDocument()
      })
    })
  })
})
