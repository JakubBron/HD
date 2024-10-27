DELETE FROM TransportyZlecenia;
DELETE FROM Zlecenia;
DELETE FROM Gabaryty;
DELETE FROM Placowki;
DELETE FROM Statusy;
GO


DECLARE @path NVARCHAR(MAX) = N'C:/Users/Ptryb/HD/Lab02/t1/';
DECLARE @sql NVARCHAR(MAX);

USE "HD_Zlecenia";

SET @sql = 'BULK INSERT Gabaryty FROM ''' + @path + 'gabaryty.csv'' WITH (CODEPAGE = ''65001'', FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'')';
EXEC sp_executesql @sql;

SET @sql = 'BULK INSERT Placowki FROM ''' + @path + 'placowki.csv'' WITH (CODEPAGE = ''65001'', FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'')';
EXEC sp_executesql @sql;

SET @sql = 'BULK INSERT Statusy FROM ''' + @path + 'statusy.csv'' WITH (CODEPAGE = ''65001'', FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'')';
EXEC sp_executesql @sql;

SET @sql = 'BULK INSERT Zlecenia FROM ''' + @path + 'zlecenia.csv'' WITH (CODEPAGE = ''65001'', FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'')';
EXEC sp_executesql @sql;

SET @sql = 'BULK INSERT TransportyZlecenia FROM ''' + @path + 'transportyzlecenia.csv'' WITH (CODEPAGE = ''65001'', FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'')';
EXEC sp_executesql @sql;