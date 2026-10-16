
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

00603e10 <.text+0x202e10>:
  603e10:	55                   	push   ebp
  603e11:	8b ec                	mov    ebp,esp
  603e13:	83 ec 08             	sub    esp,0x8
  603e16:	68 06 32 40 00       	push   0x403206
  603e1b:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  603e21:	50                   	push   eax
  603e22:	64 89 25 00 00 00 00 	mov    DWORD PTR fs:0x0,esp
  603e29:	81 ec 4c 01 00 00    	sub    esp,0x14c
  603e2f:	53                   	push   ebx
  603e30:	56                   	push   esi
  603e31:	57                   	push   edi
  603e32:	89 65 f8             	mov    DWORD PTR [ebp-0x8],esp
  603e35:	c7 45 fc b8 2a 40 00 	mov    DWORD PTR [ebp-0x4],0x402ab8
  603e3c:	8b 75 08             	mov    esi,DWORD PTR [ebp+0x8]
  603e3f:	33 c0                	xor    eax,eax
  603e41:	b9 23 00 00 00       	mov    ecx,0x23
  603e46:	8d bd 3c ff ff ff    	lea    edi,[ebp-0xc4]
  603e4c:	f3 ab                	rep stos DWORD PTR es:[edi],eax
  603e4e:	b9 23 00 00 00       	mov    ecx,0x23
  603e53:	8d bd b0 fe ff ff    	lea    edi,[ebp-0x150]
  603e59:	89 45 e0             	mov    DWORD PTR [ebp-0x20],eax
  603e5c:	89 45 dc             	mov    DWORD PTR [ebp-0x24],eax
  603e5f:	89 45 d8             	mov    DWORD PTR [ebp-0x28],eax
  603e62:	89 45 d4             	mov    DWORD PTR [ebp-0x2c],eax
  603e65:	89 45 d0             	mov    DWORD PTR [ebp-0x30],eax
  603e68:	89 45 c8             	mov    DWORD PTR [ebp-0x38],eax
  603e6b:	f3 ab                	rep stos DWORD PTR es:[edi],eax
  603e6d:	8b 0e                	mov    ecx,DWORD PTR [esi]
  603e6f:	8d 45 cc             	lea    eax,[ebp-0x34]
  603e72:	50                   	push   eax
  603e73:	51                   	push   ecx
  603e74:	c7 45 cc 01 00 00 00 	mov    DWORD PTR [ebp-0x34],0x1
  603e7b:	e8 d0 e4 ff ff       	call   0x602350
  603e80:	8b 3d 3c 12 40 00    	mov    edi,DWORD PTR ds:0x40123c
  603e86:	8b d0                	mov    edx,eax
  603e88:	8d 4d e0             	lea    ecx,[ebp-0x20]
  603e8b:	ff d7                	call   edi
  603e8d:	8b 06                	mov    eax,DWORD PTR [esi]
  603e8f:	8d 55 cc             	lea    edx,[ebp-0x34]
  603e92:	52                   	push   edx
  603e93:	50                   	push   eax
  603e94:	c7 45 cc 02 00 00 00 	mov    DWORD PTR [ebp-0x34],0x2
  603e9b:	e8 b0 e4 ff ff       	call   0x602350
  603ea0:	8b d0                	mov    edx,eax
  603ea2:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  603ea5:	ff d7                	call   edi
  603ea7:	50                   	push   eax
  603ea8:	ff 15 8c 12 40 00    	call   DWORD PTR ds:0x40128c
  603eae:	ff 15 28 12 40 00    	call   DWORD PTR ds:0x401228
  603eb4:	8b 35 80 12 40 00    	mov    esi,DWORD PTR ds:0x401280
  603eba:	8b d8                	mov    ebx,eax
  603ebc:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  603ebf:	89 5d e8             	mov    DWORD PTR [ebp-0x18],ebx
  603ec2:	ff d6                	call   esi
  603ec4:	85 db                	test   ebx,ebx
  603ec6:	7f 0a                	jg     0x603ed2
  603ec8:	c7 45 e8 01 00 00 00 	mov    DWORD PTR [ebp-0x18],0x1
  603ecf:	8b 5d e8             	mov    ebx,DWORD PTR [ebp-0x18]
  603ed2:	8b 4d e0             	mov    ecx,DWORD PTR [ebp-0x20]
  603ed5:	51                   	push   ecx
  603ed6:	68 50 ea 40 00       	push   0x40ea50
  603edb:	ff 15 0c 11 40 00    	call   DWORD PTR ds:0x40110c
  603ee1:	85 c0                	test   eax,eax
  603ee3:	0f 84 6d 01 00 00    	je     0x604056
  603ee9:	8b 1d d8 11 40 00    	mov    ebx,DWORD PTR ds:0x4011d8
  603eef:	c7 45 ec 01 00 00 00 	mov    DWORD PTR [ebp-0x14],0x1
  603ef6:	66 8b 55 ec          	mov    dx,WORD PTR [ebp-0x14]
  603efa:	66 3b 55 e8          	cmp    dx,WORD PTR [ebp-0x18]
  603efe:	0f 8f 1e 02 00 00    	jg     0x604122
  603f04:	e8 57 87 ff ff       	call   0x5fc660
  603f09:	8b f8                	mov    edi,eax
  603f0b:	66 85 ff             	test   di,di
  603f0e:	7c 5f                	jl     0x603f6f
  603f10:	8d 85 3c ff ff ff    	lea    eax,[ebp-0xc4]
  603f16:	50                   	push   eax
  603f17:	68 d0 bb 40 00       	push   0x40bbd0
  603f1c:	ff 15 94 10 40 00    	call   DWORD PTR ds:0x401094
  603f22:	ba 74 6d 41 00       	mov    edx,0x416d74
  603f27:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  603f2a:	ff d3                	call   ebx
  603f2c:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  603f2f:	8d 55 e0             	lea    edx,[ebp-0x20]
  603f32:	51                   	push   ecx
  603f33:	8d 85 3c ff ff ff    	lea    eax,[ebp-0xc4]
  603f39:	52                   	push   edx
  603f3a:	50                   	push   eax
  603f3b:	e8 40 89 ff ff       	call   0x5fc880
  603f40:	8d 8d 3c ff ff ff    	lea    ecx,[ebp-0xc4]
  603f46:	51                   	push   ecx
  603f47:	0f bf cf             	movsx  ecx,di
  603f4a:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  603f51:	2b c1                	sub    eax,ecx
  603f53:	8d 14 80             	lea    edx,[eax+eax*4]
  603f56:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  603f5b:	8d 0c 90             	lea    ecx,[eax+edx*4]
  603f5e:	51                   	push   ecx
  603f5f:	68 d0 bb 40 00       	push   0x40bbd0
  603f64:	ff 15 88 12 40 00    	call   DWORD PTR ds:0x401288
  603f6a:	e9 b8 00 00 00       	jmp    0x604027
  603f6f:	8d 95 b0 fe ff ff    	lea    edx,[ebp-0x150]
  603f75:	52                   	push   edx
  603f76:	68 d0 bb 40 00       	push   0x40bbd0
  603f7b:	ff 15 94 10 40 00    	call   DWORD PTR ds:0x401094
  603f81:	ba 74 6d 41 00       	mov    edx,0x416d74
  603f86:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  603f89:	ff d3                	call   ebx
  603f8b:	8d 45 d4             	lea    eax,[ebp-0x2c]
  603f8e:	8d 4d e0             	lea    ecx,[ebp-0x20]
  603f91:	50                   	push   eax
  603f92:	8d 95 b0 fe ff ff    	lea    edx,[ebp-0x150]
  603f98:	51                   	push   ecx
  603f99:	52                   	push   edx
  603f9a:	e8 e1 88 ff ff       	call   0x5fc880
  603f9f:	a1 ac c8 63 00       	mov    eax,ds:0x63c8ac
  603fa4:	8b 3d 10 12 40 00    	mov    edi,DWORD PTR ds:0x401210
  603faa:	8d 4d d8             	lea    ecx,[ebp-0x28]
  603fad:	50                   	push   eax
  603fae:	51                   	push   ecx
  603faf:	ff d7                	call   edi
  603fb1:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  603fb7:	8d 45 dc             	lea    eax,[ebp-0x24]
  603fba:	52                   	push   edx
  603fbb:	50                   	push   eax
  603fbc:	ff d7                	call   edi
  603fbe:	0f bf 15 a4 c8 63 00 	movsx  edx,WORD PTR ds:0x63c8a4
  603fc5:	8b 7d d8             	mov    edi,DWORD PTR [ebp-0x28]
  603fc8:	8b c2                	mov    eax,edx
  603fca:	2b 47 14             	sub    eax,DWORD PTR [edi+0x14]
  603fcd:	8b c8                	mov    ecx,eax
  603fcf:	c1 e1 05             	shl    ecx,0x5
  603fd2:	2b c8                	sub    ecx,eax
  603fd4:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  603fd7:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  603fda:	8d 04 88             	lea    eax,[eax+ecx*4]
  603fdd:	8b 4f 0c             	mov    ecx,DWORD PTR [edi+0xc]
  603fe0:	8d 84 81 5e 1f 00 00 	lea    eax,[ecx+eax*4+0x1f5e]
  603fe7:	8b 4d dc             	mov    ecx,DWORD PTR [ebp-0x24]
  603fea:	50                   	push   eax
  603feb:	2b 51 14             	sub    edx,DWORD PTR [ecx+0x14]
  603fee:	8b c2                	mov    eax,edx
  603ff0:	c1 e0 05             	shl    eax,0x5
  603ff3:	2b c2                	sub    eax,edx
  603ff5:	8d 04 c0             	lea    eax,[eax+eax*8]
  603ff8:	8d 04 42             	lea    eax,[edx+eax*2]
  603ffb:	8d 14 82             	lea    edx,[edx+eax*4]
  603ffe:	8b 41 0c             	mov    eax,DWORD PTR [ecx+0xc]
  604001:	8d 8c 90 5c 1f 00 00 	lea    ecx,[eax+edx*4+0x1f5c]
  604008:	8d 95 b0 fe ff ff    	lea    edx,[ebp-0x150]
  60400e:	51                   	push   ecx
  60400f:	52                   	push   edx
  604010:	e8 eb 15 fd ff       	call   0x5d5600
  604015:	8b 3d 70 12 40 00    	mov    edi,DWORD PTR ds:0x401270
  60401b:	8d 45 dc             	lea    eax,[ebp-0x24]
  60401e:	50                   	push   eax
  60401f:	ff d7                	call   edi
  604021:	8d 4d d8             	lea    ecx,[ebp-0x28]
  604024:	51                   	push   ecx
  604025:	ff d7                	call   edi
  604027:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  60402a:	ff d6                	call   esi
  60402c:	ba e0 59 41 00       	mov    edx,0x4159e0
  604031:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  604034:	ff d3                	call   ebx
  604036:	8d 55 d4             	lea    edx,[ebp-0x2c]
  604039:	52                   	push   edx
  60403a:	e8 81 2a 03 00       	call   0x636ac0
  60403f:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  604042:	ff d6                	call   esi
  604044:	8b 4d ec             	mov    ecx,DWORD PTR [ebp-0x14]
  604047:	b8 01 00 00 00       	mov    eax,0x1
  60404c:	03 c8                	add    ecx,eax
  60404e:	89 4d ec             	mov    DWORD PTR [ebp-0x14],ecx
  604051:	e9 a0 fe ff ff       	jmp    0x603ef6
  604056:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  60405c:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  604063:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  604066:	8b c8                	mov    ecx,eax
  604068:	c1 e1 05             	shl    ecx,0x5
  60406b:	2b c8                	sub    ecx,eax
  60406d:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  604070:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  604073:	8d 04 88             	lea    eax,[eax+ecx*4]
  604076:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  604079:	8b 94 81 e0 1f 00 00 	mov    edx,DWORD PTR [ecx+eax*4+0x1fe0]
  604080:	8d 84 81 e0 1f 00 00 	lea    eax,[ecx+eax*4+0x1fe0]
  604087:	03 d3                	add    edx,ebx
  604089:	89 10                	mov    DWORD PTR [eax],edx
  60408b:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  604091:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  604098:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  60409b:	8b c8                	mov    ecx,eax
  60409d:	c1 e1 05             	shl    ecx,0x5
  6040a0:	2b c8                	sub    ecx,eax
  6040a2:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  6040a5:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  6040a8:	8d 04 88             	lea    eax,[eax+ecx*4]
  6040ab:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  6040ae:	8b 94 81 e0 1f 00 00 	mov    edx,DWORD PTR [ecx+eax*4+0x1fe0]
  6040b5:	8d 04 81             	lea    eax,[ecx+eax*4]
  6040b8:	f7 da                	neg    edx
  6040ba:	89 90 04 21 00 00    	mov    DWORD PTR [eax+0x2104],edx
  6040c0:	8b 45 e0             	mov    eax,DWORD PTR [ebp-0x20]
  6040c3:	50                   	push   eax
  6040c4:	68 4c fc 40 00       	push   0x40fc4c
  6040c9:	ff 15 80 10 40 00    	call   DWORD PTR ds:0x401080
  6040cf:	8b d0                	mov    edx,eax
  6040d1:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  6040d4:	ff d7                	call   edi
  6040d6:	50                   	push   eax
  6040d7:	53                   	push   ebx
  6040d8:	ff 15 34 10 40 00    	call   DWORD PTR ds:0x401034
  6040de:	8b d0                	mov    edx,eax
  6040e0:	8d 4d d0             	lea    ecx,[ebp-0x30]
  6040e3:	ff d7                	call   edi
  6040e5:	50                   	push   eax
  6040e6:	ff 15 80 10 40 00    	call   DWORD PTR ds:0x401080
  6040ec:	8b d0                	mov    edx,eax
  6040ee:	8d 4d e0             	lea    ecx,[ebp-0x20]
  6040f1:	ff d7                	call   edi
  6040f3:	8d 4d d0             	lea    ecx,[ebp-0x30]
  6040f6:	8d 55 d4             	lea    edx,[ebp-0x2c]
  6040f9:	51                   	push   ecx
  6040fa:	52                   	push   edx
  6040fb:	6a 02                	push   0x2
  6040fd:	ff 15 e4 11 40 00    	call   DWORD PTR ds:0x4011e4
  604103:	83 c4 0c             	add    esp,0xc
  604106:	ba 54 59 41 00       	mov    edx,0x415954
  60410b:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  60410e:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  604114:	8d 45 d4             	lea    eax,[ebp-0x2c]
  604117:	50                   	push   eax
  604118:	e8 a3 29 03 00       	call   0x636ac0
  60411d:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  604120:	ff d6                	call   esi
  604122:	e8 59 33 fd ff       	call   0x5d7480
  604127:	8d 4d c8             	lea    ecx,[ebp-0x38]
  60412a:	8d 55 cc             	lea    edx,[ebp-0x34]
  60412d:	51                   	push   ecx
  60412e:	8d 45 e0             	lea    eax,[ebp-0x20]
  604131:	52                   	push   edx
  604132:	50                   	push   eax
  604133:	c7 45 c8 00 00 00 33 	mov    DWORD PTR [ebp-0x38],0x33000000
  60413a:	c7 45 cc 00 ff ff ff 	mov    DWORD PTR [ebp-0x34],0xffffff00
  604141:	e8 4a 34 fa ff       	call   0x5a7590
  604146:	9b                   	fwait
  604147:	68 a0 41 60 00       	push   0x6041a0
  60414c:	eb 26                	jmp    0x604174
  60414e:	8b 35 70 12 40 00    	mov    esi,DWORD PTR ds:0x401270
  604154:	8d 4d dc             	lea    ecx,[ebp-0x24]
  604157:	51                   	push   ecx
  604158:	ff d6                	call   esi
  60415a:	8d 55 d8             	lea    edx,[ebp-0x28]
  60415d:	52                   	push   edx
  60415e:	ff d6                	call   esi
  604160:	8d 45 d0             	lea    eax,[ebp-0x30]
  604163:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  604166:	50                   	push   eax
  604167:	51                   	push   ecx
  604168:	6a 02                	push   0x2
  60416a:	ff 15 e4 11 40 00    	call   DWORD PTR ds:0x4011e4
  604170:	83 c4 0c             	add    esp,0xc
  604173:	c3                   	ret
  604174:	8b 35 94 10 40 00    	mov    esi,DWORD PTR ds:0x401094
  60417a:	8d 95 3c ff ff ff    	lea    edx,[ebp-0xc4]
  604180:	52                   	push   edx
  604181:	68 d0 bb 40 00       	push   0x40bbd0
  604186:	ff d6                	call   esi
  604188:	8d 85 b0 fe ff ff    	lea    eax,[ebp-0x150]
  60418e:	50                   	push   eax
  60418f:	68 d0 bb 40 00       	push   0x40bbd0
  604194:	ff d6                	call   esi
  604196:	8d 4d e0             	lea    ecx,[ebp-0x20]
  604199:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  60419f:	c3                   	ret
  6041a0:	8b 4d f0             	mov    ecx,DWORD PTR [ebp-0x10]
  6041a3:	5f                   	pop    edi
  6041a4:	5e                   	pop    esi
  6041a5:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  6041ac:	5b                   	pop    ebx
  6041ad:	8b e5                	mov    esp,ebp
  6041af:	5d                   	pop    ebp
  6041b0:	c2 04 00             	ret    0x4
  6041b3:	90                   	nop
  6041b4:	90                   	nop
  6041b5:	90                   	nop
  6041b6:	90                   	nop
  6041b7:	90                   	nop
  6041b8:	90                   	nop
  6041b9:	90                   	nop
  6041ba:	90                   	nop
  6041bb:	90                   	nop
  6041bc:	90                   	nop
  6041bd:	90                   	nop
  6041be:	90                   	nop
  6041bf:	90                   	nop
