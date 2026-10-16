
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

00582c50 <.text+0x181c50>:
  582c50:	55                   	push   ebp
  582c51:	8b ec                	mov    ebp,esp
  582c53:	83 ec 0c             	sub    esp,0xc
  582c56:	68 06 32 40 00       	push   0x403206
  582c5b:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  582c61:	50                   	push   eax
  582c62:	64 89 25 00 00 00 00 	mov    DWORD PTR fs:0x0,esp
  582c69:	81 ec 80 00 00 00    	sub    esp,0x80
  582c6f:	53                   	push   ebx
  582c70:	56                   	push   esi
  582c71:	57                   	push   edi
  582c72:	89 65 f4             	mov    DWORD PTR [ebp-0xc],esp
  582c75:	c7 45 f8 00 1c 40 00 	mov    DWORD PTR [ebp-0x8],0x401c00
  582c7c:	8b 75 08             	mov    esi,DWORD PTR [ebp+0x8]
  582c7f:	8b c6                	mov    eax,esi
  582c81:	83 e0 01             	and    eax,0x1
  582c84:	89 45 fc             	mov    DWORD PTR [ebp-0x4],eax
  582c87:	83 e6 fe             	and    esi,0xfffffffe
  582c8a:	56                   	push   esi
  582c8b:	89 75 08             	mov    DWORD PTR [ebp+0x8],esi
  582c8e:	8b 0e                	mov    ecx,DWORD PTR [esi]
  582c90:	ff 51 04             	call   DWORD PTR [ecx+0x4]
  582c93:	8b 16                	mov    edx,DWORD PTR [esi]
  582c95:	33 db                	xor    ebx,ebx
  582c97:	56                   	push   esi
  582c98:	89 5d e8             	mov    DWORD PTR [ebp-0x18],ebx
  582c9b:	89 5d e4             	mov    DWORD PTR [ebp-0x1c],ebx
  582c9e:	89 5d e0             	mov    DWORD PTR [ebp-0x20],ebx
  582ca1:	89 5d dc             	mov    DWORD PTR [ebp-0x24],ebx
  582ca4:	89 5d cc             	mov    DWORD PTR [ebp-0x34],ebx
  582ca7:	89 5d bc             	mov    DWORD PTR [ebp-0x44],ebx
  582caa:	89 5d ac             	mov    DWORD PTR [ebp-0x54],ebx
  582cad:	89 5d 9c             	mov    DWORD PTR [ebp-0x64],ebx
  582cb0:	89 5d 8c             	mov    DWORD PTR [ebp-0x74],ebx
  582cb3:	89 5d 88             	mov    DWORD PTR [ebp-0x78],ebx
  582cb6:	ff 92 24 04 00 00    	call   DWORD PTR [edx+0x424]
  582cbc:	50                   	push   eax
  582cbd:	8d 45 e4             	lea    eax,[ebp-0x1c]
  582cc0:	50                   	push   eax
  582cc1:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  582cc7:	8b f8                	mov    edi,eax
  582cc9:	8d 55 88             	lea    edx,[ebp-0x78]
  582ccc:	52                   	push   edx
  582ccd:	57                   	push   edi
  582cce:	8b 0f                	mov    ecx,DWORD PTR [edi]
  582cd0:	ff 91 98 00 00 00    	call   DWORD PTR [ecx+0x98]
  582cd6:	3b c3                	cmp    eax,ebx
  582cd8:	db e2                	fnclex
  582cda:	7d 12                	jge    0x582cee
  582cdc:	68 98 00 00 00       	push   0x98
  582ce1:	68 b4 d5 40 00       	push   0x40d5b4
  582ce6:	57                   	push   edi
  582ce7:	50                   	push   eax
  582ce8:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582cee:	33 c0                	xor    eax,eax
  582cf0:	66 83 7d 88 ff       	cmp    WORD PTR [ebp-0x78],0xffff
  582cf5:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  582cf8:	0f 94 c0             	sete   al
  582cfb:	f7 d8                	neg    eax
  582cfd:	66 8b f8             	mov    di,ax
  582d00:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  582d06:	66 3b fb             	cmp    di,bx
  582d09:	0f 85 9c 02 00 00    	jne    0x582fab
  582d0f:	8b 0e                	mov    ecx,DWORD PTR [esi]
  582d11:	56                   	push   esi
  582d12:	ff 91 74 05 00 00    	call   DWORD PTR [ecx+0x574]
  582d18:	8d 55 dc             	lea    edx,[ebp-0x24]
  582d1b:	50                   	push   eax
  582d1c:	52                   	push   edx
  582d1d:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  582d23:	89 85 7c ff ff ff    	mov    DWORD PTR [ebp-0x84],eax
  582d29:	a1 4c 35 64 00       	mov    eax,ds:0x64354c
  582d2e:	3b c3                	cmp    eax,ebx
  582d30:	75 10                	jne    0x582d42
  582d32:	68 4c 35 64 00       	push   0x64354c
  582d37:	68 14 cd 40 00       	push   0x40cd14
  582d3c:	ff 15 c0 11 40 00    	call   DWORD PTR ds:0x4011c0
  582d42:	8d 5d e4             	lea    ebx,[ebp-0x1c]
  582d45:	b9 0a 00 00 00       	mov    ecx,0xa
  582d4a:	53                   	push   ebx
  582d4b:	89 4d cc             	mov    DWORD PTR [ebp-0x34],ecx
  582d4e:	83 ec 10             	sub    esp,0x10
  582d51:	ba 04 00 02 80       	mov    edx,0x80020004
  582d56:	8b dc                	mov    ebx,esp
  582d58:	8b c2                	mov    eax,edx
  582d5a:	83 ec 10             	sub    esp,0x10
  582d5d:	89 55 d4             	mov    DWORD PTR [ebp-0x2c],edx
  582d60:	89 0b                	mov    DWORD PTR [ebx],ecx
  582d62:	8b 4d 90             	mov    ecx,DWORD PTR [ebp-0x70]
  582d65:	8b 35 4c 35 64 00    	mov    esi,DWORD PTR ds:0x64354c
  582d6b:	89 4b 04             	mov    DWORD PTR [ebx+0x4],ecx
  582d6e:	8b cc                	mov    ecx,esp
  582d70:	83 ec 10             	sub    esp,0x10
  582d73:	8b 3e                	mov    edi,DWORD PTR [esi]
  582d75:	89 43 08             	mov    DWORD PTR [ebx+0x8],eax
  582d78:	8b 45 98             	mov    eax,DWORD PTR [ebp-0x68]
  582d7b:	89 43 0c             	mov    DWORD PTR [ebx+0xc],eax
  582d7e:	b8 0a 00 00 00       	mov    eax,0xa
  582d83:	89 01                	mov    DWORD PTR [ecx],eax
  582d85:	8b 45 a0             	mov    eax,DWORD PTR [ebp-0x60]
  582d88:	89 41 04             	mov    DWORD PTR [ecx+0x4],eax
  582d8b:	b8 0a 00 00 00       	mov    eax,0xa
  582d90:	89 51 08             	mov    DWORD PTR [ecx+0x8],edx
  582d93:	8b 55 a8             	mov    edx,DWORD PTR [ebp-0x58]
  582d96:	89 51 0c             	mov    DWORD PTR [ecx+0xc],edx
  582d99:	8b 55 b0             	mov    edx,DWORD PTR [ebp-0x50]
  582d9c:	8b cc                	mov    ecx,esp
  582d9e:	83 ec 10             	sub    esp,0x10
  582da1:	89 01                	mov    DWORD PTR [ecx],eax
  582da3:	b8 04 00 02 80       	mov    eax,0x80020004
  582da8:	89 51 04             	mov    DWORD PTR [ecx+0x4],edx
  582dab:	8b 55 c0             	mov    edx,DWORD PTR [ebp-0x40]
  582dae:	89 41 08             	mov    DWORD PTR [ecx+0x8],eax
  582db1:	8b 45 b8             	mov    eax,DWORD PTR [ebp-0x48]
  582db4:	89 41 0c             	mov    DWORD PTR [ecx+0xc],eax
  582db7:	8b cc                	mov    ecx,esp
  582db9:	b8 0a 00 00 00       	mov    eax,0xa
  582dbe:	83 ec 10             	sub    esp,0x10
  582dc1:	89 01                	mov    DWORD PTR [ecx],eax
  582dc3:	b8 04 00 02 80       	mov    eax,0x80020004
  582dc8:	89 51 04             	mov    DWORD PTR [ecx+0x4],edx
  582dcb:	8b 55 cc             	mov    edx,DWORD PTR [ebp-0x34]
  582dce:	89 41 08             	mov    DWORD PTR [ecx+0x8],eax
  582dd1:	8b 45 c8             	mov    eax,DWORD PTR [ebp-0x38]
  582dd4:	89 41 0c             	mov    DWORD PTR [ecx+0xc],eax
  582dd7:	8b 45 d0             	mov    eax,DWORD PTR [ebp-0x30]
  582dda:	8b cc                	mov    ecx,esp
  582ddc:	56                   	push   esi
  582ddd:	89 11                	mov    DWORD PTR [ecx],edx
  582ddf:	8b 55 d4             	mov    edx,DWORD PTR [ebp-0x2c]
  582de2:	89 41 04             	mov    DWORD PTR [ecx+0x4],eax
  582de5:	8b 45 d8             	mov    eax,DWORD PTR [ebp-0x28]
  582de8:	89 51 08             	mov    DWORD PTR [ecx+0x8],edx
  582deb:	89 41 0c             	mov    DWORD PTR [ecx+0xc],eax
  582dee:	ff 57 44             	call   DWORD PTR [edi+0x44]
  582df1:	33 db                	xor    ebx,ebx
  582df3:	3b c3                	cmp    eax,ebx
  582df5:	db e2                	fnclex
  582df7:	7d 0f                	jge    0x582e08
  582df9:	6a 44                	push   0x44
  582dfb:	68 04 cd 40 00       	push   0x40cd04
  582e00:	56                   	push   esi
  582e01:	50                   	push   eax
  582e02:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582e08:	8b 45 e4             	mov    eax,DWORD PTR [ebp-0x1c]
  582e0b:	8b b5 7c ff ff ff    	mov    esi,DWORD PTR [ebp-0x84]
  582e11:	8d 4d e0             	lea    ecx,[ebp-0x20]
  582e14:	50                   	push   eax
  582e15:	89 5d e4             	mov    DWORD PTR [ebp-0x1c],ebx
  582e18:	8b 3e                	mov    edi,DWORD PTR [esi]
  582e1a:	51                   	push   ecx
  582e1b:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  582e21:	50                   	push   eax
  582e22:	56                   	push   esi
  582e23:	ff 57 5c             	call   DWORD PTR [edi+0x5c]
  582e26:	3b c3                	cmp    eax,ebx
  582e28:	db e2                	fnclex
  582e2a:	7d 0f                	jge    0x582e3b
  582e2c:	6a 5c                	push   0x5c
  582e2e:	68 6c cd 40 00       	push   0x40cd6c
  582e33:	56                   	push   esi
  582e34:	50                   	push   eax
  582e35:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582e3b:	8d 55 dc             	lea    edx,[ebp-0x24]
  582e3e:	8d 45 e0             	lea    eax,[ebp-0x20]
  582e41:	52                   	push   edx
  582e42:	50                   	push   eax
  582e43:	6a 02                	push   0x2
  582e45:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  582e4b:	83 c4 0c             	add    esp,0xc
  582e4e:	66 39 1d 6a c7 63 00 	cmp    WORD PTR ds:0x63c76a,bx
  582e55:	0f 8c 50 01 00 00    	jl     0x582fab
  582e5b:	e8 90 96 07 00       	call   0x5fc4f0
  582e60:	66 85 c0             	test   ax,ax
  582e63:	75 2c                	jne    0x582e91
  582e65:	ba 08 ff 40 00       	mov    edx,0x40ff08
  582e6a:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582e6d:	89 5d 88             	mov    DWORD PTR [ebp-0x78],ebx
  582e70:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  582e76:	8d 4d 88             	lea    ecx,[ebp-0x78]
  582e79:	8d 55 e8             	lea    edx,[ebp-0x18]
  582e7c:	51                   	push   ecx
  582e7d:	52                   	push   edx
  582e7e:	e8 1d 08 07 00       	call   0x5f36a0
  582e83:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582e86:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  582e8c:	e9 1a 01 00 00       	jmp    0x582fab
  582e91:	0f bf 0d 6a c7 63 00 	movsx  ecx,WORD PTR ds:0x63c76a
  582e98:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  582e9f:	2b c1                	sub    eax,ecx
  582ea1:	8b 0d c0 ed 63 00    	mov    ecx,DWORD PTR ds:0x63edc0
  582ea7:	8d 04 80             	lea    eax,[eax+eax*4]
  582eaa:	8d 34 81             	lea    esi,[ecx+eax*4]
  582ead:	e8 3e 97 07 00       	call   0x5fc5f0
  582eb2:	66 2b 86 80 00 00 00 	sub    ax,WORD PTR [esi+0x80]
  582eb9:	79 0a                	jns    0x582ec5
  582ebb:	89 5d 88             	mov    DWORD PTR [ebp-0x78],ebx
  582ebe:	ba 20 ff 40 00       	mov    edx,0x40ff20
  582ec3:	eb 3e                	jmp    0x582f03
  582ec5:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  582ecb:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  582ed2:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  582ed5:	8b c8                	mov    ecx,eax
  582ed7:	c1 e1 05             	shl    ecx,0x5
  582eda:	2b c8                	sub    ecx,eax
  582edc:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  582edf:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  582ee2:	8d 04 88             	lea    eax,[eax+ecx*4]
  582ee5:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  582ee8:	8b 96 84 00 00 00    	mov    edx,DWORD PTR [esi+0x84]
  582eee:	8d 8c 81 e0 1f 00 00 	lea    ecx,[ecx+eax*4+0x1fe0]
  582ef5:	8b 01                	mov    eax,DWORD PTR [ecx]
  582ef7:	3b c2                	cmp    eax,edx
  582ef9:	7d 2c                	jge    0x582f27
  582efb:	89 5d 88             	mov    DWORD PTR [ebp-0x78],ebx
  582efe:	ba 38 ff 40 00       	mov    edx,0x40ff38
  582f03:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582f06:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  582f0c:	8d 55 88             	lea    edx,[ebp-0x78]
  582f0f:	8d 45 e8             	lea    eax,[ebp-0x18]
  582f12:	52                   	push   edx
  582f13:	50                   	push   eax
  582f14:	e8 87 07 07 00       	call   0x5f36a0
  582f19:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582f1c:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  582f22:	e9 84 00 00 00       	jmp    0x582fab
  582f27:	2b c2                	sub    eax,edx
  582f29:	68 4c ff 40 00       	push   0x40ff4c
  582f2e:	89 01                	mov    DWORD PTR [ecx],eax
  582f30:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  582f36:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  582f3d:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  582f40:	8b c8                	mov    ecx,eax
  582f42:	c1 e1 05             	shl    ecx,0x5
  582f45:	2b c8                	sub    ecx,eax
  582f47:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  582f4a:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  582f4d:	8d 04 88             	lea    eax,[eax+ecx*4]
  582f50:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  582f53:	8b 94 81 e0 1f 00 00 	mov    edx,DWORD PTR [ecx+eax*4+0x1fe0]
  582f5a:	8d 04 81             	lea    eax,[ecx+eax*4]
  582f5d:	f7 da                	neg    edx
  582f5f:	89 90 04 21 00 00    	mov    DWORD PTR [eax+0x2104],edx
  582f65:	0f bf 0d 6a c7 63 00 	movsx  ecx,WORD PTR ds:0x63c76a
  582f6c:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  582f73:	2b c1                	sub    eax,ecx
  582f75:	8b 0d c0 ed 63 00    	mov    ecx,DWORD PTR ds:0x63edc0
  582f7b:	8d 04 80             	lea    eax,[eax+eax*4]
  582f7e:	8b 54 81 2c          	mov    edx,DWORD PTR [ecx+eax*4+0x2c]
  582f82:	52                   	push   edx
  582f83:	ff 15 80 10 40 00    	call   DWORD PTR ds:0x401080
  582f89:	8b d0                	mov    edx,eax
  582f8b:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582f8e:	ff 15 3c 12 40 00    	call   DWORD PTR ds:0x40123c
  582f94:	8d 45 e8             	lea    eax,[ebp-0x18]
  582f97:	50                   	push   eax
  582f98:	e8 73 0e 08 00       	call   0x603e10
  582f9d:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582fa0:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  582fa6:	e8 d5 44 05 00       	call   0x5d7480
  582fab:	89 5d fc             	mov    DWORD PTR [ebp-0x4],ebx
  582fae:	68 d7 2f 58 00       	push   0x582fd7
  582fb3:	eb 21                	jmp    0x582fd6
  582fb5:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582fb8:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  582fbe:	8d 4d dc             	lea    ecx,[ebp-0x24]
  582fc1:	8d 55 e0             	lea    edx,[ebp-0x20]
  582fc4:	51                   	push   ecx
  582fc5:	8d 45 e4             	lea    eax,[ebp-0x1c]
  582fc8:	52                   	push   edx
  582fc9:	50                   	push   eax
  582fca:	6a 03                	push   0x3
  582fcc:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  582fd2:	83 c4 10             	add    esp,0x10
  582fd5:	c3                   	ret
  582fd6:	c3                   	ret
  582fd7:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  582fda:	50                   	push   eax
  582fdb:	8b 08                	mov    ecx,DWORD PTR [eax]
  582fdd:	ff 51 08             	call   DWORD PTR [ecx+0x8]
  582fe0:	8b 45 fc             	mov    eax,DWORD PTR [ebp-0x4]
  582fe3:	8b 4d ec             	mov    ecx,DWORD PTR [ebp-0x14]
  582fe6:	5f                   	pop    edi
  582fe7:	5e                   	pop    esi
  582fe8:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  582fef:	5b                   	pop    ebx
  582ff0:	8b e5                	mov    esp,ebp
  582ff2:	5d                   	pop    ebp
  582ff3:	c2 14 00             	ret    0x14
  582ff6:	90                   	nop
  582ff7:	90                   	nop
  582ff8:	90                   	nop
  582ff9:	90                   	nop
  582ffa:	90                   	nop
  582ffb:	90                   	nop
  582ffc:	90                   	nop
  582ffd:	90                   	nop
  582ffe:	90                   	nop
  582fff:	90                   	nop
