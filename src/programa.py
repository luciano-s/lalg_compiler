'''
program correto;
int a, b, c;
boolean d, e, f;

procedure proc(var a1 : int);
int a, b, c;
boolean d, e, f;
begin
	a:=1;
	if (a<1)
		a:=12
end;

begin
	a:=2;
	b:=10;
	c:=11;
	a:=b+c;
	d:=true;
	e:=false;
	f:=true;
	read(a);
	write(b);
	if (d)
	begin
		a:=20;
		b:=10*c;
		c:=a div b
	end;
	while (a>1)
	begin
		if (b>10)
			b:=2;
		a:=a-1
	end
end.
'''




program correto;
int a, b, c;
boolean d, e, f;

procedure proc(var a1 : int);
int a, b, c;
boolean d, e, f;
begin
	a:=1;
	if (a<1)
		a:=12
end;

begin
	a:=2;
	b:=10;
	c:=11;
	a:=b+c;
	d:=true;
	e:=false;
	f:=true;
	if (d)
	begin
		a:=20;
		b:=10*c;
		c:=a div b
	end;
	while (a>1) do
	begin
		if (b>10)
			b:=2;
		a:=a-1
	end
end.
